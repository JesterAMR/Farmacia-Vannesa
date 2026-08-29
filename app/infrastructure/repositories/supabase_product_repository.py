# app/infrastructure/repositories/supabase_product_repository.py
from typing import List, Optional
from app.domain.models.product import Product
from app.application.interfaces.product_repository import ProductRepositoryInterface
from app.infrastructure.database.supabase_connection import get_supabase_client

class SupabaseProductRepository(ProductRepositoryInterface):
    def __init__(self):
        self.db = get_supabase_client()

    def get_all(self, include_inactive: bool = False) -> List[Product]:
        query = self.db.table('products').select('*')
        if not include_inactive:
            query = query.eq('is_active', True)
        response = query.execute()
        products = []
        for row in response.data:
            products.append(Product(
                id=row.get('id'),
                name=row.get('name'),
                generic_name=row.get('generic_name'),
                product_code=row.get('product_code'),
                description=row.get('description'),
                stock=row.get('stock'),
                presentation=row.get('presentation'),
                laboratory=row.get('laboratory'),
                expiration_date=row.get('expiration_date'),
                dose=row.get('dose'),
                cost_price=row.get('cost_price'),
                sale_price=row.get('sale_price'),
                is_active=row.get('is_active', True)
            ))
        return products

    def get_by_id(self, product_id: int) -> Optional[Product]:
        response = self.db.table('products').select('*').eq('id', product_id).execute()
        if not response.data:
            return None
        row = response.data[0]
        return Product(
            id=row.get('id'),
            name=row.get('name'),
            generic_name=row.get('generic_name'),
            product_code=row.get('product_code'),
            description=row.get('description'),
            stock=row.get('stock'),
            presentation=row.get('presentation'),
            laboratory=row.get('laboratory'),
            expiration_date=row.get('expiration_date'),
            dose=row.get('dose'),
            cost_price=row.get('cost_price'),
            sale_price=row.get('sale_price'),
            is_active=row.get('is_active', True)
        )

    def add(self, product: Product) -> Product:
        data = {
            "name": product.name,
            "generic_name": product.generic_name,
            "product_code": product.product_code,
            "description": product.description,
            "stock": product.stock,
            "presentation": product.presentation,
            "laboratory": product.laboratory,
            "expiration_date": product.expiration_date,
            "dose": product.dose,
            "cost_price": product.cost_price,
            "sale_price": product.sale_price,
            "is_active": product.is_active
        }
        if product.id is not None:
            data["id"] = product.id
            
        response = self.db.table('products').insert(data).execute()
        if response.data:
            product.id = response.data[0].get('id')
        return product

    def update(self, product: Product) -> Product:
        data = {
            "name": product.name,
            "generic_name": product.generic_name,
            "product_code": product.product_code,
            "description": product.description,
            "stock": product.stock,
            "presentation": product.presentation,
            "laboratory": product.laboratory,
            "expiration_date": product.expiration_date,
            "dose": product.dose,
            "cost_price": product.cost_price,
            "sale_price": product.sale_price,
            "is_active": product.is_active
        }
        self.db.table('products').update(data).eq('id', product.id).execute()
        return product

    def delete(self, id: int) -> bool:
        response = self.db.table('products').update({"is_active": False}).eq('id', id).execute()
        return len(response.data) > 0