# app/infrastructure/repositories/supabase_sale_repository.py
import logging
import os
from typing import List, Optional
from app.domain.models.sale import Sale, SaleItem
from app.application.interfaces.sale_repository import SaleRepositoryInterface
from app.infrastructure.database.supabase_connection import get_supabase_client
from app.infrastructure.database.sqlite_connection import SQLiteDatabase
from app.infrastructure.repositories.sqlite_sale_repository import SQLiteSaleRepository

logger = logging.getLogger(__name__)

class SupabaseSaleRepository(SaleRepositoryInterface):
    def __init__(self):
        try:
            self.db = get_supabase_client()
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase client: {e}")
            self.db = None
            
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(base_dir, 'vannesa_db.sqlite')
        self._sqlite_repo = SQLiteSaleRepository(SQLiteDatabase(db_path=db_path))

    def get_all(self) -> List[Sale]:
        if self.db:
            try:
                response = self.db.table('sales').select('*, items:sale_items(*)').execute()
                sales = []
                for row in response.data:
                    items = []
                    for item_row in row.get('items', []):
                        items.append(SaleItem(
                            id=item_row.get('id'),
                            sale_id=item_row.get('sale_id'),
                            product_id=item_row.get('product_id'),
                            quantity=item_row.get('quantity'),
                            price=item_row.get('price'),
                            subtotal=item_row.get('subtotal')
                        ))
                    sale = Sale(
                        id=row.get('id'),
                        total=row.get('total'),
                        date=row.get('date'),
                        client_id=row.get('client_id'),
                        items=items
                    )
                    sales.append(sale)
                return sales
            except Exception as e:
                logger.warning(f"Supabase error in get_all sales: {e}. Falling back to SQLite.")
        return self._sqlite_repo.get_all()

    def get_by_id(self, sale_id: int) -> Optional[Sale]:
        if self.db:
            try:
                response = self.db.table('sales').select('*, items:sale_items(*)').eq('id', sale_id).execute()
                if not response.data:
                    return None
                row = response.data[0]
                items = []
                for item_row in row.get('items', []):
                    items.append(SaleItem(
                        id=item_row.get('id'),
                        sale_id=item_row.get('sale_id'),
                        product_id=item_row.get('product_id'),
                        quantity=item_row.get('quantity'),
                        price=item_row.get('price'),
                        subtotal=item_row.get('subtotal')
                    ))
                return Sale(
                    id=row.get('id'),
                    total=row.get('total'),
                    date=row.get('date'),
                    client_id=row.get('client_id'),
                    items=items
                )
            except Exception as e:
                logger.warning(f"Supabase error in get_by_id sale: {e}. Falling back to SQLite.")
        return self._sqlite_repo.get_by_id(sale_id)

    def add(self, sale: Sale) -> Sale:
        if self.db:
            try:
                sale_data = {
                    "total": sale.total,
                    "date": sale.date,
                    "client_id": sale.client_id
                }
                if sale.id is not None:
                    sale_data["id"] = sale.id
                    
                sale_response = self.db.table('sales').insert(sale_data).execute()
                
                if sale_response.data:
                    sale.id = sale_response.data[0].get('id')
                    if sale.items:
                        items_data = []
                        for item in sale.items:
                            item_payload = {
                                "sale_id": sale.id,
                                "product_id": item.product_id,
                                "quantity": item.quantity,
                                "price": item.price,
                                "subtotal": item.subtotal
                            }
                            if item.id is not None:
                                item_payload["id"] = item.id
                            items_data.append(item_payload)
                            
                        items_response = self.db.table('sale_items').insert(items_data).execute()
                        for idx, item_res in enumerate(items_response.data):
                            sale.items[idx].id = item_res.get('id')
                            sale.items[idx].sale_id = sale.id
                return sale
            except Exception as e:
                logger.warning(f"Supabase error in add sale: {e}. Falling back to SQLite.")
        return self._sqlite_repo.add(sale)

    def delete(self, sale_id: int) -> bool:
        if self.db:
            try:
                response = self.db.table('sales').delete().eq('id', sale_id).execute()
                return len(response.data) > 0
            except Exception as e:
                logger.warning(f"Supabase error in delete sale: {e}. Falling back to SQLite.")
        return False