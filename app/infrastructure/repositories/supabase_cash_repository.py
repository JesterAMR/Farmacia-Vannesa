from typing import List, Optional, Dict, Any
from app.infrastructure.database.supabase_connection import get_supabase_client

class SupabaseCashRepository:
    def __init__(self):
        self.db = get_supabase_client()

    # --- TURNOS / CAJA (cash_shifts) ---
    def get_active_shift(self) -> Optional[Dict[str, Any]]:
        try:
            res = self.db.table('cash_shifts').select('*, users(username)').eq('status', 'Abierta').order('id', desc=True).limit(1).execute()
            if res.data:
                shift = res.data[0]
                user_dict = shift.get('users')
                shift['username'] = user_dict.get('username', 'Cajero') if user_dict else 'Cajero'
                return shift
        except Exception as e:
            print(f"Error fetching active shift: {e}")
        return None

    def open_shift(self, shift_data: Dict[str, Any]) -> Dict[str, Any]:
        res = self.db.table('cash_shifts').insert(shift_data).execute()
        return res.data[0] if res.data else {}

    def close_shift(self, shift_id: int, closing_data: Dict[str, Any]) -> Dict[str, Any]:
        res = self.db.table('cash_shifts').update(closing_data).eq('id', shift_id).execute()
        return res.data[0] if res.data else {}

    def get_recent_shifts(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            res = self.db.table('cash_shifts').select('*, users(username)').order('id', desc=True).limit(limit).execute()
            shifts = []
            for row in res.data:
                user_dict = row.get('users')
                row['username'] = user_dict.get('username', 'Cajero') if user_dict else 'Cajero'
                shifts.append(row)
            return shifts
        except Exception as e:
            print(f"Error fetching recent shifts: {e}")
            return []

    # --- MOVIMIENTOS DE CAJA (cash_movements) ---
    def add_movement(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self.db.table('cash_movements').insert(data).execute()
        return res.data[0] if res.data else {}

    def get_all_movements(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            res = self.db.table('cash_movements').select('*, users(username)').order('id', desc=True).limit(limit).execute()
            movs = []
            for row in res.data:
                user_dict = row.get('users')
                row['username'] = user_dict.get('username', 'Cajero') if user_dict else 'Cajero'
                movs.append(row)
            return movs
        except Exception as e:
            print(f"Error fetching cash movements: {e}")
            return []

    def get_movements_summary(self) -> Dict[str, float]:
        try:
            res = self.db.table('cash_movements').select('movement_type, amount').execute()
            total_in = 0.0
            total_out = 0.0
            total_vault = 0.0
            for r in res.data:
                amt = float(r.get('amount') or 0.0)
                mtype = r.get('movement_type', '')
                if mtype == 'Ingreso':
                    total_in += amt
                elif mtype == 'Egreso':
                    total_out += amt
                elif 'Retiro' in mtype or 'Bóveda' in mtype or 'Boveda' in mtype:
                    total_vault += amt
            return {
                "total_in": total_in,
                "total_out": total_out,
                "total_vault": total_vault,
                "balance": total_in - total_out - total_vault
            }
        except Exception as e:
            print(f"Error calculating cash summary: {e}")
            return {"total_in": 0.0, "total_out": 0.0, "total_vault": 0.0, "balance": 0.0}
