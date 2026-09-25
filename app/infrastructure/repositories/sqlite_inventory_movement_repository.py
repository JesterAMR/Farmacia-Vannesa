import sqlite3
from typing import List, Optional
from datetime import datetime
from app.domain.models.inventory_movement import InventoryMovement
from app.application.interfaces.inventory_movement_repository import InventoryMovementRepositoryInterface
from app.infrastructure.database.sqlite_connection import SQLiteDatabase

class SQLiteInventoryMovementRepository(InventoryMovementRepositoryInterface):
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def add(self, movement: InventoryMovement) -> InventoryMovement:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("""
                INSERT INTO inventory_movements (product_id, user_id, movement_type, quantity, previous_stock, new_stock, reason, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (movement.product_id, movement.user_id, movement.movement_type, movement.quantity,
                  movement.previous_stock, movement.new_stock, movement.reason, movement.notes, now_str))
            conn.commit()
            movement.id = cursor.lastrowid
            movement.created_at = now_str
            return movement

    def get_all(self, limit: int = 100) -> List[InventoryMovement]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.*, p.name as product_name, p.product_code, p.presentation, u.username 
                FROM inventory_movements m
                LEFT JOIN products p ON m.product_id = p.id
                LEFT JOIN users u ON m.user_id = u.id
                ORDER BY m.id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [
                InventoryMovement(
                    id=row['id'],
                    product_id=row['product_id'],
                    user_id=row['user_id'],
                    username=row['username'] or "admin",
                    product_name=row['product_name'] or "Medicamento",
                    product_code=row['product_code'] or f"MED-{row['product_id']:03d}",
                    presentation=row['presentation'] or "Estándar",
                    movement_type=row['movement_type'],
                    quantity=row['quantity'],
                    previous_stock=row['previous_stock'],
                    new_stock=row['new_stock'],
                    reason=row['reason'],
                    notes=row['notes'],
                    created_at=row['created_at']
                ) for row in rows
            ]

    def get_by_product_id(self, product_id: int, limit: int = 50) -> List[InventoryMovement]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.*, p.name as product_name, p.product_code, p.presentation, u.username 
                FROM inventory_movements m
                LEFT JOIN products p ON m.product_id = p.id
                LEFT JOIN users u ON m.user_id = u.id
                WHERE m.product_id = ?
                ORDER BY m.id DESC LIMIT ?
            """, (product_id, limit))
            rows = cursor.fetchall()
            return [
                InventoryMovement(
                    id=row['id'],
                    product_id=row['product_id'],
                    user_id=row['user_id'],
                    username=row['username'] or "admin",
                    product_name=row['product_name'] or "Medicamento",
                    product_code=row['product_code'] or f"MED-{row['product_id']:03d}",
                    presentation=row['presentation'] or "Estándar",
                    movement_type=row['movement_type'],
                    quantity=row['quantity'],
                    previous_stock=row['previous_stock'],
                    new_stock=row['new_stock'],
                    reason=row['reason'],
                    notes=row['notes'],
                    created_at=row['created_at']
                ) for row in rows
            ]

    def get_metrics(self) -> dict:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inventory_movements")
            total_movements = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(quantity) FROM inventory_movements WHERE LOWER(movement_type) = 'entrada'")
            total_entries = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(ABS(quantity)) FROM inventory_movements WHERE LOWER(movement_type) = 'salida'")
            total_exits = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(ABS(quantity)) FROM inventory_movements WHERE LOWER(movement_type) LIKE '%merma%' OR LOWER(movement_type) LIKE '%ajuste%'")
            total_losses = cursor.fetchone()[0] or 0

            return {
                "total_movements": total_movements,
                "total_entries": total_entries,
                "total_exits": total_exits,
                "total_losses": total_losses
            }
