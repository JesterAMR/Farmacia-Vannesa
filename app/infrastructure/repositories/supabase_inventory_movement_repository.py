from typing import List, Optional, Dict, Any
from app.infrastructure.database.supabase_connection import get_supabase_client

class SupabaseInventoryMovementRepository:
    def __init__(self):
        self.db = get_supabase_client()

    def add_movement(self, movement_data: Dict[str, Any]) -> Dict[str, Any]:
        res = self.db.table('inventory_movements').insert(movement_data).execute()
        return res.data[0] if res.data else {}

    def get_all_movements(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            res = self.db.table('inventory_movements').select('*, products(name, product_code, presentation), users(username)').order('id', desc=True).limit(limit).execute()
            movements = []
            for row in res.data:
                prod = row.get('products') or {}
                usr = row.get('users') or {}
                row['product_name'] = prod.get('name', 'Medicamento')
                row['product_code'] = prod.get('product_code', 'N/A')
                row['presentation'] = prod.get('presentation', '')
                row['username'] = usr.get('username', 'admin')
                
                # Assign badge class
                mtype = row.get('movement_type', '')
                if mtype == 'Entrada':
                    row['badge_class'] = 'badge-entry'
                elif mtype == 'Salida':
                    row['badge_class'] = 'badge-exit'
                else:
                    row['badge_class'] = 'badge-adj'
                    
                movements.append(row)
            return movements
        except Exception as e:
            print(f"Error fetching inventory movements: {e}")
            return []

    def get_metrics(self) -> Dict[str, int]:
        try:
            res = self.db.table('inventory_movements').select('movement_type, quantity').execute()
            total_entries = 0
            total_exits = 0
            total_losses = 0
            for r in res.data:
                mtype = r.get('movement_type', '')
                qty = abs(int(r.get('quantity') or 0))
                if mtype == 'Entrada':
                    total_entries += qty
                elif mtype == 'Salida':
                    total_exits += qty
                else:
                    total_losses += qty
            return {
                "total_movements": len(res.data),
                "total_entries": total_entries,
                "total_exits": total_exits,
                "total_losses": total_losses
            }
        except Exception as e:
            print(f"Error computing movement metrics: {e}")
            return {"total_movements": 0, "total_entries": 0, "total_exits": 0, "total_losses": 0}
