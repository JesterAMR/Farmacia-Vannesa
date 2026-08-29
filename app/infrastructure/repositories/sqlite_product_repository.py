import sqlite3
from typing import List, Optional
from app.domain.models.product import Product
from app.application.interfaces.product_repository import ProductRepositoryInterface
from app.infrastructure.database.sqlite_connection import SQLiteDatabase

class SQLiteProductRepository(ProductRepositoryInterface):
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def _row_to_product(self, row) -> Product:
        is_active = True
        try:
            is_active = bool(row['is_active'])
        except Exception:
            pass
        return Product(
            id=row['id'],
            name=row['name'],
            generic_name=row['generic_name'],
            product_code=row['product_code'],
            description=row['description'],
            stock=row['stock'],
            presentation=row['presentation'],
            laboratory=row['laboratory'],
            expiration_date=row['expiration_date'],
            dose=row['dose'],
            cost_price=row['cost_price'],
            sale_price=row['sale_price'],
            is_active=is_active
        )

    def add(self, product: Product) -> Product:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO products 
                   (name, generic_name, product_code, description, 
                    stock, presentation, laboratory, expiration_date, dose, 
                    cost_price, sale_price, is_active) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (product.name, product.generic_name, product.product_code, product.description,
                 product.stock, product.presentation, product.laboratory, product.expiration_date, product.dose,
                 product.cost_price, product.sale_price, 1 if product.is_active else 0)
            )
            conn.commit()
            product.id = cursor.lastrowid
            return product

    def get_by_id(self, id: int) -> Optional[Product]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?", (id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_product(row)
            return None

    def get_all(self, include_inactive: bool = False) -> List[Product]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if include_inactive:
                cursor.execute("SELECT * FROM products")
            else:
                cursor.execute("SELECT * FROM products WHERE is_active = 1")
            rows = cursor.fetchall()
            return [self._row_to_product(row) for row in rows]

    def update(self, product: Product) -> Product:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE products SET 
                   name = ?, generic_name = ?, product_code = ?, description = ?, 
                   stock = ?, presentation = ?, laboratory = ?, expiration_date = ?, dose = ?, 
                   cost_price = ?, sale_price = ?, is_active = ? 
                   WHERE id = ?""",
                (product.name, product.generic_name, product.product_code, product.description,
                 product.stock, product.presentation, product.laboratory, product.expiration_date, product.dose,
                 product.cost_price, product.sale_price, 1 if product.is_active else 0, product.id)
            )
            conn.commit()
            return product

    def delete(self, id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET is_active = 0 WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
