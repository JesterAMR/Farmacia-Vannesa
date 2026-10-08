# app/infrastructure/repositories/supabase_sale_repository.py
import os
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
                total=float(row.get('total') or 0.0),
                date=row.get('date', ''),
                client_id=row.get('client_id'),
                items=items,
                subtotal_exempt=float(row.get('subtotal_exempt') or 0.0),
                subtotal_taxable=float(row.get('subtotal_taxable') or 0.0),
                iva_total=float(row.get('iva_total') or 0.0),
                currency=row.get('currency') or 'NIO',
                exchange_rate=float(row.get('exchange_rate') or 36.62),
                total_usd=float(row.get('total_usd') or 0.0),
                prescription_doctor=row.get('prescription_doctor'),
                doctor_minsa_code=row.get('doctor_minsa_code'),
                prescription_number=row.get('prescription_number'),
                fiscal_xml=row.get('fiscal_xml'),
                dgi_auth_number=row.get('dgi_auth_number')
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
                    price=float(item_row.get('price') or 0.0),
                    subtotal=float(item_row.get('subtotal') or 0.0)
                ))
            return Sale(
                id=row.get('id'),
                total=float(row.get('total') or 0.0),
                date=row.get('date', ''),
                client_id=row.get('client_id'),
                items=items,
                subtotal_exempt=float(row.get('subtotal_exempt') or 0.0),
                subtotal_taxable=float(row.get('subtotal_taxable') or 0.0),
                iva_total=float(row.get('iva_total') or 0.0),
                currency=row.get('currency') or 'NIO',
                exchange_rate=float(row.get('exchange_rate') or 36.62),
                total_usd=float(row.get('total_usd') or 0.0),
                prescription_doctor=row.get('prescription_doctor'),
                doctor_minsa_code=row.get('doctor_minsa_code'),
                prescription_number=row.get('prescription_number'),
                fiscal_xml=row.get('fiscal_xml'),
                dgi_auth_number=row.get('dgi_auth_number')
            )
        except Exception as e:
            logging.error(f"[SupabaseSaleRepository] Error get_by_id ({sale_id}): {e}")
            return None

    def add(self, sale: Sale) -> Sale:
        sale_data = {
            "total": sale.total,
            "date": sale.date,
            "client_id": sale.client_id,
            "subtotal_exempt": sale.subtotal_exempt,
            "subtotal_taxable": sale.subtotal_taxable,
            "iva_total": sale.iva_total,
            "currency": sale.currency,
            "exchange_rate": sale.exchange_rate,
            "total_usd": sale.total_usd,
            "prescription_doctor": sale.prescription_doctor,
            "doctor_minsa_code": sale.doctor_minsa_code,
            "prescription_number": sale.prescription_number,
            "fiscal_xml": sale.fiscal_xml,
            "dgi_auth_number": sale.dgi_auth_number
        }
        if sale.id is not None:
            sale_data["id"] = sale.id
            
        try:
            sale_response = self.db.table('sales').insert(sale_data).execute()
        except Exception as e:
            logging.warning(f"[SupabaseSaleRepository] Retrying insert with legacy payload: {e}")
            # Si faltan columnas MINSA/DGI en Supabase, reintentar sin ellas de forma segura
            legacy_keys = ["subtotal_exempt", "subtotal_taxable", "iva_total", "currency", 
                           "exchange_rate", "total_usd", "prescription_doctor", 
                           "doctor_minsa_code", "prescription_number", "fiscal_xml", "dgi_auth_number"]
            for k in legacy_keys:
                sale_data.pop(k, None)
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

    def delete(self, sale_id: int) -> bool:
        try:
            response = self.db.table('sales').delete().eq('id', sale_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logging.error(f"[SupabaseSaleRepository] Error delete ({sale_id}): {e}")
            return False
