from typing import List, Dict, Any, Optional
import logging
from app.domain.models.sale import Sale, SaleItem
from app.domain.models.product import Product
from app.application.interfaces.sale_repository import SaleRepositoryInterface
from app.application.interfaces.product_repository import ProductRepositoryInterface

logger = logging.getLogger(__name__)

class SalesService:
    def __init__(self, sale_repository: SaleRepositoryInterface, 
                 product_repository: ProductRepositoryInterface,
                 inventory_movement_service=None,
                 cash_service=None):
        self._sale_repository = sale_repository
        self._product_repository = product_repository
        self._inventory_movement_service = inventory_movement_service
        self._cash_service = cash_service

    def create_sale(self, items_data: List[Dict[str, Any]], client_id: Optional[int] = None, user_id: Optional[int] = None) -> Sale:
        if not items_data:
            raise ValueError("No hay artículos en la venta.")

        # Phase 1: Pre-validation of all items and stocks before any deduction (ACID preparation)
        prepared_items = []
        for item_data in items_data:
            prod_id = item_data.get('product_id')
            qty = item_data.get('quantity', 0)
            
            product = self._product_repository.get_by_id(prod_id)
            if not product:
                raise ValueError(f"Producto {prod_id} no encontrado en catálogo.")

            if qty <= 0:
                raise ValueError(f"La cantidad vendida para {product.name} debe ser mayor a cero.")

            if product.stock < qty:
                raise ValueError(f"Stock insuficiente para {product.name}. Stock actual: {product.stock}, solicitado: {qty}")

            prepared_items.append({
                "product": product,
                "qty": qty,
                "subtotal": product.price * qty
            })

        # Phase 2: Deduct stock with rollback protection
        deducted_rollback_list = []
        sale_items = []
        total = 0.0

        try:
            for item in prepared_items:
                product = item["product"]
                qty = item["qty"]
                original_stock = product.stock

                # Deduct stock
                product.stock -= qty
                self._product_repository.update(product)
                deducted_rollback_list.append((product, original_stock))

                sale_items.append(SaleItem(
                    product_id=product.id,
                    quantity=qty,
                    price=product.price,
                    subtotal=item["subtotal"]
                ))
                total += item["subtotal"]

            sale = Sale(total=total, items=sale_items, client_id=client_id)
            created_sale = self._sale_repository.add(sale)

            # Phase 3: Automatic Kardex and Cash integrations
            if self._inventory_movement_service:
                for item in prepared_items:
                    try:
                        self._inventory_movement_service.register_movement(
                            product_id=item["product"].id,
                            movement_type="Salida",
                            quantity=item["qty"],
                            reason=f"Venta en Mostrador #{created_sale.id}",
                            user_id=user_id,
                            update_stock=False
                        )
                    except Exception as me:
                        logger.warning(f"Error registrando movimiento de Kardex para venta: {me}")

            if self._cash_service:
                try:
                    open_shift = self._cash_service.get_open_shift()
                    if open_shift:
                        self._cash_service.add_movement(
                            movement_type="Ingreso",
                            concept=f"Cobro de Venta #{created_sale.id}",
                            amount=total,
                            category="Ventas",
                            voucher=f"V-{created_sale.id:04d}",
                            user_id=user_id
                        )
                except Exception as ce:
                    logger.warning(f"Error registrando ingreso de caja para venta: {ce}")

            return created_sale

        except Exception as e:
            # Rollback any stock deductions if sale creation failed
            for product, original_stock in deducted_rollback_list:
                try:
                    product.stock = original_stock
                    self._product_repository.update(product)
                except Exception as rbe:
                    logger.critical(f"Error durante rollback de stock: {rbe}")
            raise e

    def get_all_sales(self) -> List[Sale]:
        return self._sale_repository.get_all()

    def get_sale(self, id: int) -> Optional[Sale]:
        return self._sale_repository.get_by_id(id)
