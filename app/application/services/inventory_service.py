from typing import List, Optional
from app.domain.models.product import Product
from app.application.interfaces.product_repository import ProductRepositoryInterface

class InventoryService:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self._product_repository = product_repository

    def create_product(self, name: str, generic_name: str, product_code: str, description: str,
                       stock: int, presentation: str, laboratory: str, expiration_date: str, dose: str,
                       cost_price: float, sale_price: float) -> Product:
        
        # Validate unique product code
        existing_products = self._product_repository.get_all(include_inactive=True)
        for p in existing_products:
            if p.product_code and p.product_code.strip().lower() == product_code.strip().lower():
                raise ValueError(f"El código de producto '{product_code}' ya existe en el sistema.")

        product = Product(
            name=name, generic_name=generic_name, product_code=product_code, description=description,
            stock=stock, presentation=presentation, laboratory=laboratory, 
            expiration_date=expiration_date, dose=dose,
            cost_price=cost_price, sale_price=sale_price
        )
        return self._product_repository.add(product)

    def get_product(self, id: int) -> Optional[Product]:
        return self._product_repository.get_by_id(id)

    def get_all_products(self, include_inactive: bool = False) -> List[Product]:
        return self._product_repository.get_all(include_inactive=include_inactive)

    def update_product(self, product: Product) -> Product:
        # Validate unique product code for other products
        existing_products = self._product_repository.get_all(include_inactive=True)
        for p in existing_products:
            if p.id != product.id and p.product_code and p.product_code.strip().lower() == product.product_code.strip().lower():
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
