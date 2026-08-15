import sqlite3
from typing import List, Optional
from app.domain.models.sale import Sale, SaleItem
from app.application.interfaces.sale_repository import SaleRepositoryInterface
from app.infrastructure.database.sqlite_connection import SQLiteDatabase

class SQLiteSaleRepository(SaleRepositoryInterface):
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def add(self, sale: Sale) -> Sale:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Insert sale
            cursor.execute(
                "INSERT INTO sales (total, date, client_id) VALUES (?, ?, ?)",
                (sale.total, sale.date, sale.client_id)
            )
            sale.id = cursor.lastrowid
            
            # Insert items
            for item in sale.items:
                cursor.execute(
                    "INSERT INTO sale_items (sale_id, product_id, quantity, price, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (sale.id, item.product_id, item.quantity, item.price, item.subtotal)
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
                
            cursor.execute("SELECT * FROM sale_items WHERE sale_id = ?", (id,))
            item_rows = cursor.fetchall()
            
            items = [
                SaleItem(
                    id=row['id'],
                    sale_id=row['sale_id'],
                    product_id=row['product_id'],
                    quantity=row['quantity'],
                    price=row['price'],
                    subtotal=row['subtotal']
                ) for row in item_rows
            ]
            
            return Sale(
                id=sale_row['id'],
                total=sale_row['total'],
                date=sale_row['date'],
                client_id=sale_row['client_id'],
                items=items
            )

    def get_all(self) -> List[Sale]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sales ORDER BY id DESC")
            sale_rows = cursor.fetchall()
            
            sales = []
            for sale_row in sale_rows:
                sale_id = sale_row['id']
                cursor.execute("SELECT * FROM sale_items WHERE sale_id = ?", (sale_id,))
                item_rows = cursor.fetchall()
                
                items = [
                    SaleItem(
                        id=row['id'],
                        sale_id=row['sale_id'],
                        product_id=row['product_id'],
                        quantity=row['quantity'],
                        price=row['price'],
                        subtotal=row['subtotal']
                    ) for row in item_rows
                ]
                
                sales.append(Sale(
                    id=sale_id,
                    total=sale_row['total'],
                    date=sale_row['date'],
                    client_id=sale_row['client_id'],
                    items=items
                ))
                
            return sales
