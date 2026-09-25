import sqlite3
from typing import List, Optional
from datetime import datetime
from app.domain.models.cash import CashShift, CashMovement
from app.application.interfaces.cash_repository import CashRepositoryInterface
from app.infrastructure.database.sqlite_connection import SQLiteDatabase

class SQLiteCashRepository(CashRepositoryInterface):
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def get_open_shift(self) -> Optional[CashShift]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, u.username as cashier_username 
                FROM cash_shifts s
                LEFT JOIN users u ON s.user_id = u.id
                WHERE s.status = 'Abierta'
                ORDER BY s.id DESC LIMIT 1
            """)
            row = cursor.fetchone()
            if not row:
                return None
            return CashShift(
                id=row['id'],
                user_id=row['user_id'],
                cashier_username=row['cashier_username'] or "Cajero",
                shift_name=row['shift_name'],
                register_name=row['register_name'],
                initial_amount=float(row['initial_amount'] or 0.0),
                expected_cash=float(row['expected_cash']) if row['expected_cash'] is not None else None,
                physical_cash=float(row['physical_cash']) if row['physical_cash'] is not None else None,
                difference=float(row['difference']) if row['difference'] is not None else None,
                vault_deposit=float(row['vault_deposit']) if row['vault_deposit'] is not None else None,
                remnant_cash=float(row['remnant_cash']) if row['remnant_cash'] is not None else None,
                status=row['status'],
                notes=row['notes'],
                opened_at=row['opened_at'],
                closed_at=row['closed_at']
            )

    def open_shift(self, shift: CashShift) -> CashShift:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("""
                INSERT INTO cash_shifts (user_id, shift_name, register_name, initial_amount, status, notes, opened_at)
                VALUES (?, ?, ?, ?, 'Abierta', ?, ?)
            """, (shift.user_id, shift.shift_name, shift.register_name, shift.initial_amount, shift.notes, now_str))
            conn.commit()
            shift.id = cursor.lastrowid
            shift.opened_at = now_str
            shift.status = 'Abierta'
            return shift

    def close_shift(self, shift_id: int, physical_cash: float, expected_cash: float, 
                    difference: float, notes: Optional[str] = None) -> Optional[CashShift]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("""
                UPDATE cash_shifts
                SET status = 'Cerrada',
                    physical_cash = ?,
                    expected_cash = ?,
                    difference = ?,
                    closed_at = ?,
                    notes = COALESCE(?, notes)
                WHERE id = ?
            """, (physical_cash, expected_cash, difference, now_str, notes, shift_id))
            conn.commit()
            return self.get_by_id(shift_id)

    def get_by_id(self, shift_id: int) -> Optional[CashShift]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, u.username as cashier_username 
                FROM cash_shifts s
                LEFT JOIN users u ON s.user_id = u.id
                WHERE s.id = ?
            """, (shift_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return CashShift(
                id=row['id'],
                user_id=row['user_id'],
                cashier_username=row['cashier_username'] or "Cajero",
                shift_name=row['shift_name'],
                register_name=row['register_name'],
                initial_amount=float(row['initial_amount'] or 0.0),
                expected_cash=float(row['expected_cash']) if row['expected_cash'] is not None else None,
                physical_cash=float(row['physical_cash']) if row['physical_cash'] is not None else None,
                difference=float(row['difference']) if row['difference'] is not None else None,
                vault_deposit=float(row['vault_deposit']) if row['vault_deposit'] is not None else None,
                remnant_cash=float(row['remnant_cash']) if row['remnant_cash'] is not None else None,
                status=row['status'],
                notes=row['notes'],
                opened_at=row['opened_at'],
                closed_at=row['closed_at']
            )

    def get_recent_shifts(self, limit: int = 10) -> List[CashShift]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, u.username as cashier_username 
                FROM cash_shifts s
                LEFT JOIN users u ON s.user_id = u.id
                ORDER BY s.id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(CashShift(
                    id=row['id'],
                    user_id=row['user_id'],
                    cashier_username=row['cashier_username'] or "Cajero",
                    shift_name=row['shift_name'],
                    register_name=row['register_name'],
                    initial_amount=float(row['initial_amount'] or 0.0),
                    expected_cash=float(row['expected_cash']) if row['expected_cash'] is not None else None,
                    physical_cash=float(row['physical_cash']) if row['physical_cash'] is not None else None,
                    difference=float(row['difference']) if row['difference'] is not None else None,
                    status=row['status'],
                    notes=row['notes'],
                    opened_at=row['opened_at'],
                    closed_at=row['closed_at']
                ))
            return result

    def add_movement(self, movement: CashMovement) -> CashMovement:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("""
                INSERT INTO cash_movements (shift_id, user_id, movement_type, category, concept, amount, voucher_reference, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (movement.shift_id, movement.user_id, movement.movement_type, movement.category,
                  movement.concept, movement.amount, movement.voucher_reference, now_str))
            conn.commit()
            movement.id = cursor.lastrowid
            movement.created_at = now_str
            return movement

    def get_movements(self, shift_id: Optional[int] = None, limit: int = 50) -> List[CashMovement]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if shift_id:
                cursor.execute("""
                    SELECT m.*, u.username 
                    FROM cash_movements m
                    LEFT JOIN users u ON m.user_id = u.id
                    WHERE m.shift_id = ?
                    ORDER BY m.id DESC LIMIT ?
                """, (shift_id, limit))
            else:
                cursor.execute("""
                    SELECT m.*, u.username 
                    FROM cash_movements m
                    LEFT JOIN users u ON m.user_id = u.id
                    ORDER BY m.id DESC LIMIT ?
                """, (limit,))
            rows = cursor.fetchall()
            return [
                CashMovement(
                    id=row['id'],
                    shift_id=row['shift_id'],
                    user_id=row['user_id'],
                    username=row['username'] or "Sistema",
                    movement_type=row['movement_type'],
                    category=row['category'],
                    concept=row['concept'],
                    amount=float(row['amount'] or 0.0),
                    voucher_reference=row['voucher_reference'],
                    created_at=row['created_at']
                ) for row in rows
            ]

    def get_financial_summary(self, shift_id: Optional[int] = None) -> dict:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Base query filter
            filter_sql = "WHERE shift_id = ?" if shift_id else ""
            params = (shift_id,) if shift_id else ()

            cursor.execute(f"SELECT SUM(amount) FROM cash_movements {filter_sql} {'AND' if shift_id else 'WHERE'} LOWER(movement_type) = 'ingreso'", params)
            total_income = cursor.fetchone()[0] or 0.0

            cursor.execute(f"SELECT SUM(amount) FROM cash_movements {filter_sql} {'AND' if shift_id else 'WHERE'} LOWER(movement_type) = 'egreso'", params)
            total_expense = cursor.fetchone()[0] or 0.0

            cursor.execute(f"SELECT SUM(amount) FROM cash_movements {filter_sql} {'AND' if shift_id else 'WHERE'} LOWER(movement_type) LIKE '%bóveda%' OR LOWER(movement_type) LIKE '%retiro%'", params)
            total_vault = cursor.fetchone()[0] or 0.0

            initial_cash = 0.0
            if shift_id:
                cursor.execute("SELECT initial_amount FROM cash_shifts WHERE id = ?", (shift_id,))
                row = cursor.fetchone()
                if row:
                    initial_cash = float(row[0] or 0.0)

            current_drawer = initial_cash + total_income - total_expense - total_vault
            return {
                "initial_cash": initial_cash,
                "total_income": total_income,
                "total_expense": total_expense,
                "total_vault": total_vault,
                "current_drawer": current_drawer
            }
