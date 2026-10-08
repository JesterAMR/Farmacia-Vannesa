import sqlite3
from typing import List, Optional, Tuple
from app.domain.models.product import Product
from app.application.interfaces.product_repository import ProductRepositoryInterface
from app.infrastructure.database.sqlite_connection import SQLiteDatabase

class SQLiteProductRepository(ProductRepositoryInterface):
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def _row_to_product(self, row) -> Product:
        is_active = True
        sanitary_register = "MINSA-REG-2024-001"
        batch_number = "LOT-GEN-01"
        is_controlled = False
        is_exempt_iva = True
        
        try:
            is_active = bool(row['is_active'])
        except Exception:
            pass

        try:
            if 'sanitary_register' in row.keys() and row['sanitary_register'] is not None:
                sanitary_register = row['sanitary_register']
        except Exception:
            pass

        try:
            if 'batch_number' in row.keys() and row['batch_number'] is not None:
                batch_number = row['batch_number']
        except Exception:
            pass

        try:
            if 'is_controlled' in row.keys() and row['is_controlled'] is not None:
                is_controlled = bool(row['is_controlled'])
        except Exception:
            pass

        try:
            if 'is_exempt_iva' in row.keys() and row['is_exempt_iva'] is not None:
                is_exempt_iva = bool(row['is_exempt_iva'])
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
            sanitary_register=sanitary_register,
            batch_number=batch_number,
            is_controlled=is_controlled,
            is_exempt_iva=is_exempt_iva,
            is_active=is_active
        )

    def add(self, product: Product) -> Product:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO products 
                   (name, generic_name, product_code, description, 
                    stock, presentation, laboratory, expiration_date, dose, 
                    cost_price, sale_price, sanitary_register, batch_number, 
                    is_controlled, is_exempt_iva, is_active) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (product.name, product.generic_name, product.product_code, product.description,
                 product.stock, product.presentation, product.laboratory, product.expiration_date, product.dose,
                 product.cost_price, product.sale_price, product.sanitary_register, product.batch_number,
                 1 if product.is_controlled else 0, 1 if product.is_exempt_iva else 0, 1 if product.is_active else 0)
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

    def get_by_code(self, product_code: str) -> Optional[Product]:
        if not product_code:
            return None
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE LOWER(TRIM(product_code)) = LOWER(TRIM(?))", (product_code,))
            row = cursor.fetchone()
            if row:
                return self._row_to_product(row)
            return None

    def get_all(self, include_inactive: bool = False) -> List[Product]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if include_inactive:
                cursor.execute("SELECT * FROM products ORDER BY name ASC")
            else:
                cursor.execute("SELECT * FROM products WHERE is_active = 1 ORDER BY name ASC")
            rows = cursor.fetchall()
            return [self._row_to_product(row) for row in rows]

    def get_paginated(self, page: int = 1, per_page: int = 10, search: Optional[str] = None, include_inactive: bool = False) -> Tuple[List[Product], int]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            where_clauses = []
            params = []

            if not include_inactive:
                where_clauses.append("is_active = 1")

            if search and search.strip():
                s = f"%{search.strip().lower()}%"
                where_clauses.append("(LOWER(name) LIKE ? OR LOWER(generic_name) LIKE ? OR LOWER(product_code) LIKE ? OR LOWER(sanitary_register) LIKE ? OR LOWER(batch_number) LIKE ?)")
                params.extend([s, s, s, s, s])

            where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
            
            # Count total
            count_query = f"SELECT COUNT(*) FROM products{where_sql}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]

            # Fetch paginated items
            offset = max(0, (page - 1) * per_page)
            data_query = f"SELECT * FROM products{where_sql} ORDER BY name ASC LIMIT ? OFFSET ?"
            cursor.execute(data_query, params + [per_page, offset])
            rows = cursor.fetchall()
            products = [self._row_to_product(row) for row in rows]

            return products, total

    def update(self, product: Product) -> Product:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE products SET 
                   name = ?, generic_name = ?, product_code = ?, description = ?, 
                   stock = ?, presentation = ?, laboratory = ?, expiration_date = ?, dose = ?, 
                   cost_price = ?, sale_price = ?, sanitary_register = ?, batch_number = ?, 
                   is_controlled = ?, is_exempt_iva = ?, is_active = ? 
                   WHERE id = ?""",
                (product.name, product.generic_name, product.product_code, product.description,
                 product.stock, product.presentation, product.laboratory, product.expiration_date, product.dose,
                 product.cost_price, product.sale_price, product.sanitary_register, product.batch_number,
                 1 if product.is_controlled else 0, 1 if product.is_exempt_iva else 0, 1 if product.is_active else 0, product.id)
            )
            conn.commit()
            return product

    def delete(self, id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET is_active = 0 WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
