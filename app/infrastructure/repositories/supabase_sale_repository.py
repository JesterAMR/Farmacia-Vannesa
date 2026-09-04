# app/infrastructure/repositories/supabase_sale_repository.py
import logging
from typing import List, Optional
from app.domain.models.sale import Sale, SaleItem
from app.application.interfaces.sale_repository import SaleRepositoryInterface
from app.infrastructure.database.supabase_connection import get_supabase_client

class SupabaseSaleRepository(SaleRepositoryInterface):
    def __init__(self):
        self.db = get_supabase_client()

    def get_all(self) -> List[Sale]:
        try:
            response = self.db.table('sales').select('*, items:sale_items(*)').execute()
        except Exception as e:
            logging.error(f"[SupabaseSaleRepository] Error get_all with items: {e}")
            try:
                response = self.db.table('sales').select('*').execute()
            except Exception as e2:
                logging.error(f"[SupabaseSaleRepository] Error fallback get_all: {e2}")
                return []

        sales = []
        for row in response.data or []:
            items = []
            for item_row in row.get('items', []) or []:
                items.append(SaleItem(
                    id=item_row.get('id'),
                    sale_id=item_row.get('sale_id'),
                    product_id=item_row.get('product_id'),
                    quantity=item_row.get('quantity', 1),
                    price=item_row.get('price', 0.0),
                    subtotal=item_row.get('subtotal', 0.0)
                ))
            sale = Sale(
                id=row.get('id'),
                total=row.get('total', 0.0),
                date=row.get('date', ''),
                client_id=row.get('client_id'),
                items=items
            )
            sales.append(sale)
        return sales

    def get_by_id(self, sale_id: int) -> Optional[Sale]:
        try:
            response = self.db.table('sales').select('*, items:sale_items(*)').eq('id', sale_id).execute()
            if not response.data:
                return None
            row = response.data[0]
            items = []
            for item_row in row.get('items', []) or []:
                items.append(SaleItem(
                    id=item_row.get('id'),
                    sale_id=item_row.get('sale_id'),
                    product_id=item_row.get('product_id'),
                    quantity=item_row.get('quantity', 1),
                    price=item_row.get('price', 0.0),
                    subtotal=item_row.get('subtotal', 0.0)
                ))
            return Sale(
                id=row.get('id'),
                total=row.get('total', 0.0),
                date=row.get('date', ''),
                client_id=row.get('client_id'),
                items=items
            )
        except Exception as e:
            logging.error(f"[SupabaseSaleRepository] Error get_by_id ({sale_id}): {e}")
            return None

    def add(self, sale: Sale) -> Sale:
        sale_data = {
            "total": sale.total,
            "date": sale.date,
            "client_id": sale.client_id
        }
        if sale.id is not None:
            sale_data["id"] = sale.id
            
        try:
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
                    for idx, item_res in enumerate(items_response.data or []):
                        if idx < len(sale.items):
                            sale.items[idx].id = item_res.get('id')
                            sale.items[idx].sale_id = sale.id
            return sale
        except Exception as e:
            logging.error(f"[SupabaseSaleRepository] Error add sale: {e}")
            raise e

    def delete(self, sale_id: int) -> bool:
        try:
            response = self.db.table('sales').delete().eq('id', sale_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logging.error(f"[SupabaseSaleRepository] Error delete ({sale_id}): {e}")
            return False
