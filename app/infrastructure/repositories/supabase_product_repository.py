# app/infrastructure/repositories/supabase_product_repository.py
import logging
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
        try:
            query = self.db.table('products').select('*')
            if not include_inactive:
                query = query.eq('is_active', True)
            response = query.execute()
        except Exception as e:
            logging.warning(f"[SupabaseProductRepository] Error with is_active filter: {e}. Trying select('*').")
            try:
                response = self.db.table('products').select('*').execute()
            except Exception as e2:
                logging.error(f"[SupabaseProductRepository] Error fallback select: {e2}")
                return []

        products = []
        for row in response.data or []:
            raw_active = row.get('is_active')
            is_active = True if raw_active is None else bool(raw_active)

            if not include_inactive and not is_active:
                        continue

            products.append(Product(
                id=row.get('id'),
                name=row.get('name', 'Sin Nombre'),
                generic_name=row.get('generic_name', ''),
                product_code=row.get('product_code', ''),
                description=row.get('description', ''),
                stock=int(row.get('stock') or 0),
                presentation=row.get('presentation', ''),
                laboratory=row.get('laboratory', ''),
                expiration_date=row.get('expiration_date', ''),
                dose=row.get('dose', ''),
                cost_price=float(row.get('cost_price') or 0.0),
                sale_price=float(row.get('sale_price') or 0.0),
                is_active=is_active
            ))
        return products

    def get_by_id(self, product_id: int) -> Optional[Product]:
        try:
            response = self.db.table('products').select('*').eq('id', product_id).execute()
            if not response.data:
                return None
            row = response.data[0]
            raw_active = row.get('is_active')
            is_active = True if raw_active is None else bool(raw_active)

            return Product(
                id=row.get('id'),
                name=row.get('name', 'Sin Nombre'),
                generic_name=row.get('generic_name', ''),
                product_code=row.get('product_code', ''),
                description=row.get('description', ''),
                stock=int(row.get('stock') or 0),
                presentation=row.get('presentation', ''),
                laboratory=row.get('laboratory', ''),
                expiration_date=row.get('expiration_date', ''),
                dose=row.get('dose', ''),
                cost_price=float(row.get('cost_price') or 0.0),
                sale_price=float(row.get('sale_price') or 0.0),
                is_active=is_active
            )
        except Exception as e:
            logging.error(f"[SupabaseProductRepository] Error get_by_id ({product_id}): {e}")
            return None

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
            
        try:
            response = self.db.table('products').insert(data).execute()
        except Exception as e:
            logging.warning(f"[SupabaseProductRepository] Retrying insert without is_active: {e}")
            data.pop("is_active", None)
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
        try:
            self.db.table('products').update(data).eq('id', product.id).execute()
        except Exception as e:
            logging.warning(f"[SupabaseProductRepository] Retrying update without is_active: {e}")
            data.pop("is_active", None)
            self.db.table('products').update(data).eq('id', product.id).execute()

        return product

    def delete(self, product_id: int) -> bool:
        try:
            # Soft delete
            response = self.db.table('products').update({"is_active": False}).eq('id', product_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logging.error(f"[SupabaseProductRepository] Error in delete/soft-delete: {e}")
            return False

    def restock(self, product_id: int, quantity: int) -> Optional[Product]:
        product = self.get_by_id(product_id)
        if product:
            product.stock += quantity
            return self.update(product)
        return None
