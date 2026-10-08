import math
from typing import List, Optional, Dict, Any
from app.domain.models.product import Product
from app.application.interfaces.product_repository import ProductRepositoryInterface

class InventoryService:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self._product_repository = product_repository

    def create_product(self, name: str, generic_name: str, product_code: str, description: str,
                       stock: int, presentation: str, laboratory: str, expiration_date: str, dose: str,
                       cost_price: float, sale_price: float,
                       sanitary_register: str = "MINSA-REG-2024-001",
                       batch_number: str = "LOT-GEN-01",
                       is_controlled: bool = False,
                       is_exempt_iva: bool = True) -> Product:
        
        # Validaciones de Integridad y Normativa Nicaragüense
        if cost_price <= 0:
            raise ValueError("El precio de costo debe ser estrictamente mayor a cero.")
        if sale_price <= 0:
            raise ValueError("El precio de venta debe ser estrictamente mayor a cero.")
        if stock < 0:
            raise ValueError("El stock no puede ser un número negativo.")
        if not sanitary_register or not sanitary_register.strip():
            raise ValueError("El Registro Sanitario MINSA es obligatorio según la Ley 292.")
        if not batch_number or not batch_number.strip():
            raise ValueError("El número de lote es obligatorio para control de trazabilidad sanitaria.")

        # Validar código único de producto
        existing = self._product_repository.get_by_code(product_code)
        if existing:
            raise ValueError(f"El código de producto '{product_code}' ya existe en el sistema.")

        product = Product(
            name=name, generic_name=generic_name, product_code=product_code, description=description,
            stock=stock, presentation=presentation, laboratory=laboratory, 
            expiration_date=expiration_date, dose=dose,
            cost_price=cost_price, sale_price=sale_price,
            sanitary_register=sanitary_register.strip(),
            batch_number=batch_number.strip(),
            is_controlled=is_controlled,
            is_exempt_iva=is_exempt_iva
        )
        return self._product_repository.add(product)

    def get_product(self, id: int) -> Optional[Product]:
        return self._product_repository.get_by_id(id)

    def get_all_products(self, include_inactive: bool = False) -> List[Product]:
        return self._product_repository.get_all(include_inactive=include_inactive)

    def get_paginated_products(self, page: int = 1, per_page: int = 10, 
                               search: Optional[str] = None, 
                               include_inactive: bool = False) -> Dict[str, Any]:
        """Paginación para listados de inventario de acuerdo a los requerimientos de usabilidad."""
        page = max(1, int(page))
        per_page = max(1, min(100, int(per_page)))
        items, total = self._product_repository.get_paginated(
            page=page, per_page=per_page, search=search, include_inactive=include_inactive
        )
        total_pages = max(1, math.ceil(total / per_page))
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages,
            "prev_page": page - 1 if page > 1 else None,
            "next_page": page + 1 if page < total_pages else None
        }

    def update_product(self, product: Product) -> Product:
        existing = self._product_repository.get_by_code(product.product_code)
        if existing and existing.id != product.id:
            raise ValueError(f"El código de producto '{product.product_code}' ya pertenece a otro medicamento.")

        return self._product_repository.update(product)

    def delete_product(self, id: int) -> bool:
        return self._product_repository.delete(id)
        
    def restock_product(self, id: int, added_quantity: int) -> Optional[Product]:
        product = self._product_repository.get_by_id(id)
        if product and added_quantity > 0:
            product.stock += added_quantity
            return self._product_repository.update(product)
        return None

    def get_inventory_valuation(self):
        products = self._product_repository.get_all()
        total_items = sum(p.stock for p in products)
        total_cost_value = sum(p.stock * p.cost_price for p in products)
        total_sale_value = sum(p.stock * p.sale_price for p in products)
        
        return {
            "total_items": total_items,
            "total_cost_value": total_cost_value,
            "total_sale_value": total_sale_value,
            "total_unique_products": len(products)
        }
