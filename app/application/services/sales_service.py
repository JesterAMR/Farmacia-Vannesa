from typing import List, Dict, Any, Optional
from app.domain.models.sale import Sale, SaleItem
from app.domain.models.product import Product
from app.application.interfaces.sale_repository import SaleRepositoryInterface
from app.application.interfaces.product_repository import ProductRepositoryInterface

class SalesService:
    def __init__(self, sale_repository: SaleRepositoryInterface, product_repository: ProductRepositoryInterface):
        self._sale_repository = sale_repository
        self._product_repository = product_repository

    def create_sale(self, items_data: List[Dict[str, Any]], client_id: Optional[int] = None) -> Sale:
        # items_data contains [{'product_id': 1, 'quantity': 2}, ...]
        sale_items = []
        total = 0.0
        
        for item_data in items_data:
            product = self._product_repository.get_by_id(item_data['product_id'])
            if not product:
                raise ValueError(f"Producto {item_data['product_id']} no encontrado.")
            
            qty = item_data['quantity']
            if qty <= 0:
                raise ValueError(f"La cantidad vendida para {product.name} debe ser mayor a cero.")
                
            if product.stock < qty:
                raise ValueError(f"Stock insuficiente para {product.name}.")
                
            # Deduct stock
            product.stock -= qty
            self._product_repository.update(product)
            
            subtotal = product.price * qty
            sale_items.append(SaleItem(
                product_id=product.id,
                quantity=qty,
                price=product.price,
                subtotal=subtotal
            ))
            total += subtotal

        sale = Sale(total=total, items=sale_items, client_id=client_id)
        return self._sale_repository.add(sale)

    def get_all_sales(self) -> List[Sale]:
        return self._sale_repository.get_all()
        
    def get_sale(self, id: int) -> Optional[Sale]:
        return self._sale_repository.get_by_id(id)
