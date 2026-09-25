import logging
from typing import List, Optional
from datetime import datetime
from app.domain.models.inventory_movement import InventoryMovement
from app.application.interfaces.inventory_movement_repository import InventoryMovementRepositoryInterface
from app.infrastructure.database.supabase_connection import get_supabase_client

logger = logging.getLogger(__name__)

class SupabaseInventoryMovementRepository(InventoryMovementRepositoryInterface):
    def __init__(self):
        try:
            self.db = get_supabase_client()
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase client for InventoryMovements: {e}")
            self.db = None

    def add(self, movement: InventoryMovement) -> InventoryMovement:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        data = {
            "product_id": movement.product_id,
            "user_id": movement.user_id,
            "movement_type": movement.movement_type,
            "quantity": movement.quantity,
            "previous_stock": movement.previous_stock,
            "new_stock": movement.new_stock,
            "reason": movement.reason,
            "notes": movement.notes,
            "created_at": now_str
        }
        try:
            res = self.db.table('inventory_movements').insert(data).execute()
            if res.data:
                movement.id = res.data[0].get('id')
            movement.created_at = now_str
            return movement
        except Exception as e:
            logger.error(f"[SupabaseInventoryMovementRepository] add error: {e}")
            raise e

    def get_all(self, limit: int = 100) -> List[InventoryMovement]:
        try:
            res = self.db.table('inventory_movements').select('*, products(name, product_code, presentation), users(username)').order('id', desc=True).limit(limit).execute()
            result = []
            for row in res.data or []:
                prod_name = "Medicamento"
                prod_code = f"MED-{row.get('product_id', 0):03d}"
                presentation = "Estándar"
                if row.get('products'):
                    prod_name = row['products'].get('name', prod_name)
                    prod_code = row['products'].get('product_code', prod_code)
                    presentation = row['products'].get('presentation', presentation)

                username = "admin"
                if row.get('users'):
                    username = row['users'].get('username', 'admin')

                result.append(InventoryMovement(
                    id=row.get('id'),
                    product_id=row.get('product_id'),
                    user_id=row.get('user_id'),
                    username=username,
                    product_name=prod_name,
                    product_code=prod_code,
                    presentation=presentation,
                    movement_type=row.get('movement_type', 'Entrada'),
                    quantity=row.get('quantity', 0),
                    previous_stock=row.get('previous_stock', 0),
                    new_stock=row.get('new_stock', 0),
                    reason=row.get('reason', ''),
                    notes=row.get('notes'),
                    created_at=row.get('created_at', '')
                ))
            return result
        except Exception as e:
            logger.error(f"[SupabaseInventoryMovementRepository] get_all error: {e}")
            return []

    def get_by_product_id(self, product_id: int, limit: int = 50) -> List[InventoryMovement]:
        try:
            res = self.db.table('inventory_movements').select('*, products(name, product_code, presentation), users(username)').eq('product_id', product_id).order('id', desc=True).limit(limit).execute()
            result = []
            for row in res.data or []:
                prod_name = "Medicamento"
                prod_code = f"MED-{row.get('product_id', 0):03d}"
                presentation = "Estándar"
                if row.get('products'):
                    prod_name = row['products'].get('name', prod_name)
                    prod_code = row['products'].get('product_code', prod_code)
                    presentation = row['products'].get('presentation', presentation)

                username = "admin"
                if row.get('users'):
                    username = row['users'].get('username', 'admin')

                result.append(InventoryMovement(
                    id=row.get('id'),
                    product_id=row.get('product_id'),
                    user_id=row.get('user_id'),
                    username=username,
                    product_name=prod_name,
                    product_code=prod_code,
                    presentation=presentation,
                    movement_type=row.get('movement_type', 'Entrada'),
                    quantity=row.get('quantity', 0),
                    previous_stock=row.get('previous_stock', 0),
                    new_stock=row.get('new_stock', 0),
                    reason=row.get('reason', ''),
                    notes=row.get('notes'),
                    created_at=row.get('created_at', '')
                ))
            return result
        except Exception as e:
            logger.error(f"[SupabaseInventoryMovementRepository] get_by_product_id error: {e}")
            return []

    def get_metrics(self) -> dict:
        movements = self.get_all(limit=500)
        total_movements = len(movements)
        total_entries = sum(m.quantity for m in movements if m.movement_type.lower() == 'entrada')
        total_exits = sum(abs(m.quantity) for m in movements if m.movement_type.lower() == 'salida')
        total_losses = sum(abs(m.quantity) for m in movements if 'merma' in m.movement_type.lower() or 'ajuste' in m.movement_type.lower())

        return {
            "total_movements": total_movements,
            "total_entries": total_entries,
            "total_exits": total_exits,
            "total_losses": total_losses
        }
