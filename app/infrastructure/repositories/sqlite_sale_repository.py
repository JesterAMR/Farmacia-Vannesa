import sqlite3
from typing import List, Optional
from app.domain.models.sale import Sale, SaleItem
from app.application.interfaces.sale_repository import SaleRepositoryInterface
from app.infrastructure.database.sqlite_connection import SQLiteDatabase

class SQLiteSaleRepository(SaleRepositoryInterface):
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def _row_to_sale_item(self, row) -> SaleItem:
        is_exempt = True
        iva_rate = 0.0
        iva_amount = 0.0
        batch_number = None
        product_name = None

        try:
            if 'is_exempt' in row.keys() and row['is_exempt'] is not None:
                is_exempt = bool(row['is_exempt'])
            if 'iva_rate' in row.keys() and row['iva_rate'] is not None:
                iva_rate = float(row['iva_rate'])
            if 'iva_amount' in row.keys() and row['iva_amount'] is not None:
                iva_amount = float(row['iva_amount'])
            if 'batch_number' in row.keys():
                batch_number = row['batch_number']
            if 'product_name' in row.keys():
                product_name = row['product_name']
        except Exception:
            pass

        return SaleItem(
            id=row['id'],
            sale_id=row['sale_id'],
            product_id=row['product_id'],
            quantity=row['quantity'],
            price=row['price'],
            subtotal=row['subtotal'],
            is_exempt=is_exempt,
            iva_rate=iva_rate,
            iva_amount=iva_amount,
            batch_number=batch_number,
            product_name=product_name
        )

    def _row_to_sale(self, sale_row, items: List[SaleItem]) -> Sale:
        subtotal_exempt = 0.0
        subtotal_taxable = 0.0
        iva_total = 0.0
        currency = "NIO"
        exchange_rate = 36.62
        total_usd = 0.0
        prescription_doctor = None
        doctor_minsa_code = None
        prescription_number = None
        fiscal_xml = None
        dgi_auth_number = None

        try:
            if 'subtotal_exempt' in sale_row.keys() and sale_row['subtotal_exempt'] is not None:
                subtotal_exempt = float(sale_row['subtotal_exempt'])
            if 'subtotal_taxable' in sale_row.keys() and sale_row['subtotal_taxable'] is not None:
                subtotal_taxable = float(sale_row['subtotal_taxable'])
            if 'iva_total' in sale_row.keys() and sale_row['iva_total'] is not None:
                iva_total = float(sale_row['iva_total'])
            if 'currency' in sale_row.keys() and sale_row['currency']:
                currency = sale_row['currency']
            if 'exchange_rate' in sale_row.keys() and sale_row['exchange_rate'] is not None:
                exchange_rate = float(sale_row['exchange_rate'])
            if 'total_usd' in sale_row.keys() and sale_row['total_usd'] is not None:
                total_usd = float(sale_row['total_usd'])
            if 'prescription_doctor' in sale_row.keys():
                prescription_doctor = sale_row['prescription_doctor']
            if 'doctor_minsa_code' in sale_row.keys():
                doctor_minsa_code = sale_row['doctor_minsa_code']
            if 'prescription_number' in sale_row.keys():
                prescription_number = sale_row['prescription_number']
            if 'fiscal_xml' in sale_row.keys():
                fiscal_xml = sale_row['fiscal_xml']
            if 'dgi_auth_number' in sale_row.keys():
                dgi_auth_number = sale_row['dgi_auth_number']
        except Exception:
            pass

        return Sale(
            id=sale_row['id'],
            total=sale_row['total'],
            date=sale_row['date'],
            client_id=sale_row['client_id'],
            items=items,
            subtotal_exempt=subtotal_exempt,
            subtotal_taxable=subtotal_taxable,
            iva_total=iva_total,
            currency=currency,
            exchange_rate=exchange_rate,
            total_usd=total_usd,
            prescription_doctor=prescription_doctor,
            doctor_minsa_code=doctor_minsa_code,
            prescription_number=prescription_number,
            fiscal_xml=fiscal_xml,
            dgi_auth_number=dgi_auth_number
        )

    def add(self, sale: Sale) -> Sale:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO sales 
                   (total, date, client_id, subtotal_exempt, subtotal_taxable, iva_total, 
                    currency, exchange_rate, total_usd, prescription_doctor, doctor_minsa_code, 
                    prescription_number, fiscal_xml, dgi_auth_number) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (sale.total, sale.date, sale.client_id, sale.subtotal_exempt, sale.subtotal_taxable,
                 sale.iva_total, sale.currency, sale.exchange_rate, sale.total_usd,
                 sale.prescription_doctor, sale.doctor_minsa_code, sale.prescription_number,
                 sale.fiscal_xml, sale.dgi_auth_number)
            )
            sale.id = cursor.lastrowid
            
            # Insert items
            for item in sale.items:
                cursor.execute(
                    """INSERT INTO sale_items 
                       (sale_id, product_id, quantity, price, subtotal, is_exempt, iva_rate, iva_amount, batch_number) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (sale.id, item.product_id, item.quantity, item.price, item.subtotal,
                     1 if item.is_exempt else 0, item.iva_rate, item.iva_amount, item.batch_number)
                )
                item.id = cursor.lastrowid
                item.sale_id = sale.id
                
            conn.commit()
            return sale

    def get_by_id(self, id: int) -> Optional[Sale]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sales WHERE id = ?", (id,))
            sale_row = cursor.fetchone()
            
            if not sale_row:
                return None
                
            cursor.execute("""
                SELECT si.*, p.name as product_name 
                FROM sale_items si 
                LEFT JOIN products p ON si.product_id = p.id 
                WHERE si.sale_id = ?
            """, (id,))
            item_rows = cursor.fetchall()
            items = [self._row_to_sale_item(row) for row in item_rows]
            
            return self._row_to_sale(sale_row, items)

    def get_all(self) -> List[Sale]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sales ORDER BY id DESC")
            sale_rows = cursor.fetchall()
            
            sales = []
            for sale_row in sale_rows:
                sale_id = sale_row['id']
                cursor.execute("""
                    SELECT si.*, p.name as product_name 
                    FROM sale_items si 
                    LEFT JOIN products p ON si.product_id = p.id 
                    WHERE si.sale_id = ?
                """, (sale_id,))
                item_rows = cursor.fetchall()
                items = [self._row_to_sale_item(row) for row in item_rows]
                sales.append(self._row_to_sale(sale_row, items))
                
            return sales
