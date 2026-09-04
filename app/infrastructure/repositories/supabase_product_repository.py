# app/infrastructure/repositories/supabase_product_repository.py
import logging
import os
from typing import List, Optional
from app.domain.models.product import Product
from app.application.interfaces.product_repository import ProductRepositoryInterface
from app.infrastructure.database.supabase_connection import get_supabase_client
from app.infrastructure.database.sqlite_connection import SQLiteDatabase
from app.infrastructure.repositories.sqlite_product_repository import SQLiteProductRepository

logger = logging.getLogger(__name__)

class SupabaseProductRepository(ProductRepositoryInterface):
    def __init__(self):
        try:
            self.db = get_supabase_client()
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase client: {e}")
            self.db = None
            
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(base_dir, 'vannesa_db.sqlite')
        self._sqlite_repo = SQLiteProductRepository(SQLiteDatabase(db_path=db_path))

    def get_all(self, include_inactive: bool = False) -> List[Product]:
        if self.db:
            try:
                query = self.db.table('products').select('*')
                if not include_inactive:
                    query = query.eq('is_active', True)
                response = query.execute()

                products = []
                for row in response.data:
                    raw_active = row.get('is_active')
                    is_active = True if raw_active is None else bool(raw_active)

                    if not include_inactive and not is_active:
                        continue

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
                        is_active=is_active
                    ))
                return products
            except Exception as e:
                logger.warning(f"Supabase error in get_all products: {e}. Falling back to SQLite.")
        return self._sqlite_repo.get_all(include_inactive=include_inactive)

    def get_by_id(self, product_id: int) -> Optional[Product]:
        if self.db:
            try:
                response = self.db.table('products').select('*').eq('id', product_id).execute()
                if not response.data:
                    return None
                row = response.data[0]
                raw_active = row.get('is_active')
                is_active = True if raw_active is None else bool(raw_active)

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
                    is_active=is_active
                )
            except Exception as e:
                logger.warning(f"Supabase error in get_by_id product: {e}. Falling back to SQLite.")
        return self._sqlite_repo.get_by_id(product_id)

    def add(self, product: Product) -> Product:
        if self.db:
            try:
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
            except Exception as e:
                logger.warning(f"Supabase error in add product: {e}. Falling back to SQLite.")
        return self._sqlite_repo.add(product)

    def update(self, product: Product) -> Product:
        if self.db:
            try:
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
            except Exception as e:
                logger.warning(f"Supabase error in update product: {e}. Falling back to SQLite.")
        return self._sqlite_repo.update(product)

    def delete(self, id: int) -> bool:
        if self.db:
            try:
                response = self.db.table('products').update({"is_active": False}).eq('id', id).execute()
                if response.data:
                    return len(response.data) > 0
            except Exception as e:
                logger.warning(f"Supabase error in delete product: {e}. Falling back to SQLite.")
        return self._sqlite_repo.delete(id)