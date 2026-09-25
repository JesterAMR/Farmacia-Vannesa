import logging
from typing import List, Optional
from datetime import datetime
from app.domain.models.cash import CashShift, CashMovement
from app.application.interfaces.cash_repository import CashRepositoryInterface
from app.infrastructure.database.supabase_connection import get_supabase_client

logger = logging.getLogger(__name__)

class SupabaseCashRepository(CashRepositoryInterface):
    def __init__(self):
        try:
            self.db = get_supabase_client()
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase client for Cash: {e}")
            self.db = None

    def get_open_shift(self) -> Optional[CashShift]:
        try:
            res = self.db.table('cash_shifts').select('*, users(username)').eq('status', 'Abierta').order('id', desc=True).limit(1).execute()
            if not res.data:
                return None
            row = res.data[0]
            cashier = "Cajero"
            if row.get('users'):
                cashier = row['users'].get('username', 'Cajero')
            return CashShift(
                id=row.get('id'),
                user_id=row.get('user_id'),
                cashier_username=cashier,
                shift_name=row.get('shift_name', 'Matutino'),
                register_name=row.get('register_name', 'Caja #1 - Principal'),
                initial_amount=float(row.get('initial_amount') or 0.0),
                expected_cash=float(row['expected_cash']) if row.get('expected_cash') is not None else None,
                physical_cash=float(row['physical_cash']) if row.get('physical_cash') is not None else None,
                difference=float(row['difference']) if row.get('difference') is not None else None,
                status=row.get('status', 'Abierta'),
                notes=row.get('notes'),
                opened_at=row.get('opened_at', ''),
                closed_at=row.get('closed_at')
            )
        except Exception as e:
            logger.error(f"[SupabaseCashRepository] get_open_shift error: {e}")
            return None

    def open_shift(self, shift: CashShift) -> CashShift:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        data = {
            "user_id": shift.user_id,
            "shift_name": shift.shift_name,
            "register_name": shift.register_name,
            "initial_amount": shift.initial_amount,
            "status": "Abierta",
            "notes": shift.notes,
            "opened_at": now_str
        }
        try:
            res = self.db.table('cash_shifts').insert(data).execute()
            if res.data:
                shift.id = res.data[0].get('id')
            shift.opened_at = now_str
            shift.status = "Abierta"
            return shift
        except Exception as e:
            logger.error(f"[SupabaseCashRepository] open_shift error: {e}")
            raise e

    def close_shift(self, shift_id: int, physical_cash: float, expected_cash: float, 
                    difference: float, notes: Optional[str] = None) -> Optional[CashShift]:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        data = {
            "status": "Cerrada",
            "physical_cash": physical_cash,
            "expected_cash": expected_cash,
            "difference": difference,
            "closed_at": now_str
        }
        if notes:
            data["notes"] = notes
        try:
            self.db.table('cash_shifts').update(data).eq('id', shift_id).execute()
            return self.get_by_id(shift_id)
        except Exception as e:
            logger.error(f"[SupabaseCashRepository] close_shift error: {e}")
            return None

    def get_by_id(self, shift_id: int) -> Optional[CashShift]:
        try:
            res = self.db.table('cash_shifts').select('*, users(username)').eq('id', shift_id).execute()
            if not res.data:
                return None
            row = res.data[0]
            cashier = "Cajero"
            if row.get('users'):
                cashier = row['users'].get('username', 'Cajero')
            return CashShift(
                id=row.get('id'),
                user_id=row.get('user_id'),
                cashier_username=cashier,
                shift_name=row.get('shift_name', 'Matutino'),
                register_name=row.get('register_name', 'Caja #1 - Principal'),
                initial_amount=float(row.get('initial_amount') or 0.0),
                expected_cash=float(row['expected_cash']) if row.get('expected_cash') is not None else None,
                physical_cash=float(row['physical_cash']) if row.get('physical_cash') is not None else None,
                difference=float(row['difference']) if row.get('difference') is not None else None,
                status=row.get('status', 'Abierta'),
                notes=row.get('notes'),
                opened_at=row.get('opened_at', ''),
                closed_at=row.get('closed_at')
            )
        except Exception as e:
            logger.error(f"[SupabaseCashRepository] get_by_id error: {e}")
            return None

    def get_recent_shifts(self, limit: int = 10) -> List[CashShift]:
        try:
            res = self.db.table('cash_shifts').select('*, users(username)').order('id', desc=True).limit(limit).execute()
            result = []
            for row in res.data or []:
                cashier = "Cajero"
                if row.get('users'):
                    cashier = row['users'].get('username', 'Cajero')
                result.append(CashShift(
                    id=row.get('id'),
                    user_id=row.get('user_id'),
                    cashier_username=cashier,
                    shift_name=row.get('shift_name', 'Matutino'),
                    register_name=row.get('register_name', 'Caja #1 - Principal'),
                    initial_amount=float(row.get('initial_amount') or 0.0),
                    expected_cash=float(row['expected_cash']) if row.get('expected_cash') is not None else None,
                    physical_cash=float(row['physical_cash']) if row.get('physical_cash') is not None else None,
                    difference=float(row['difference']) if row.get('difference') is not None else None,
                    status=row.get('status', 'Abierta'),
                    notes=row.get('notes'),
                    opened_at=row.get('opened_at', ''),
                    closed_at=row.get('closed_at')
                ))
            return result
        except Exception as e:
            logger.error(f"[SupabaseCashRepository] get_recent_shifts error: {e}")
            return []

    def add_movement(self, movement: CashMovement) -> CashMovement:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        data = {
            "shift_id": movement.shift_id,
            "user_id": movement.user_id,
            "movement_type": movement.movement_type,
            "category": movement.category,
            "concept": movement.concept,
            "amount": movement.amount,
            "voucher_reference": movement.voucher_reference,
            "created_at": now_str
        }
        try:
            res = self.db.table('cash_movements').insert(data).execute()
            if res.data:
                movement.id = res.data[0].get('id')
            movement.created_at = now_str
            return movement
        except Exception as e:
            logger.error(f"[SupabaseCashRepository] add_movement error: {e}")
            raise e

    def get_movements(self, shift_id: Optional[int] = None, limit: int = 50) -> List[CashMovement]:
        try:
            q = self.db.table('cash_movements').select('*, users(username)').order('id', desc=True).limit(limit)
            if shift_id:
                q = q.eq('shift_id', shift_id)
            res = q.execute()
            result = []
            for row in res.data or []:
                username = "Sistema"
                if row.get('users'):
                    username = row['users'].get('username', 'Sistema')
                result.append(CashMovement(
                    id=row.get('id'),
                    shift_id=row.get('shift_id'),
                    user_id=row.get('user_id'),
                    username=username,
                    movement_type=row.get('movement_type', 'Operativo'),
                    category=row.get('category', 'Operativo'),
                    concept=row.get('concept', ''),
                    amount=float(row.get('amount') or 0.0),
                    voucher_reference=row.get('voucher_reference'),
                    created_at=row.get('created_at', '')
                ))
            return result
        except Exception as e:
            logger.error(f"[SupabaseCashRepository] get_movements error: {e}")
            return []

    def get_financial_summary(self, shift_id: Optional[int] = None) -> dict:
        movements = self.get_movements(shift_id=shift_id, limit=500)
        total_income = sum(m.amount for m in movements if m.movement_type.lower() == 'ingreso')
        total_expense = sum(m.amount for m in movements if m.movement_type.lower() == 'egreso')
        total_vault = sum(m.amount for m in movements if 'bóveda' in m.movement_type.lower() or 'retiro' in m.movement_type.lower())

        initial_cash = 0.0
        if shift_id:
            shift = self.get_by_id(shift_id)
            if shift:
                initial_cash = shift.initial_amount

        current_drawer = initial_cash + total_income - total_expense - total_vault
        return {
            "initial_cash": initial_cash,
            "total_income": total_income,
            "total_expense": total_expense,
            "total_vault": total_vault,
            "current_drawer": current_drawer
        }
