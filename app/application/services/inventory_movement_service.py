from typing import List, Optional
from app.domain.models.inventory_movement import InventoryMovement
from app.application.interfaces.inventory_movement_repository import InventoryMovementRepositoryInterface
from app.application.interfaces.product_repository import ProductRepositoryInterface

class InventoryMovementService:
    def __init__(self, movement_repository: InventoryMovementRepositoryInterface, 
                 product_repository: ProductRepositoryInterface):
        self._movement_repo = movement_repository
        self._product_repo = product_repository

    def register_movement(self, product_id: int, movement_type: str, quantity: int, 
                          reason: str, notes: Optional[str] = None, user_id: Optional[int] = None,
                          update_stock: bool = True) -> InventoryMovement:
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")

        product = self._product_repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"El producto con ID {product_id} no fue encontrado.")

        prev_stock = product.stock
        m_type_lower = movement_type.lower()

        if "entrada" in m_type_lower:
            new_stock = prev_stock + quantity if update_stock else prev_stock
            applied_qty = quantity
            historical_prev = prev_stock
            historical_new = new_stock
        elif "salida" in m_type_lower or "merma" in m_type_lower or "ajuste" in m_type_lower:
            if update_stock and prev_stock < quantity:
                raise ValueError(f"Stock insuficiente para {product.name}. Stock actual: {prev_stock}, solicitado: {quantity}")
            new_stock = prev_stock - quantity if update_stock else prev_stock
            applied_qty = -quantity
            historical_prev = prev_stock + quantity if not update_stock else prev_stock
            historical_new = prev_stock if not update_stock else new_stock
        else:
            raise ValueError(f"Tipo de movimiento '{movement_type}' no reconocido.")

        # Update product stock if requested
        if update_stock:
            product.stock = new_stock
            self._product_repo.update(product)

        # Record movement
        movement = InventoryMovement(
            product_id=product.id,
            user_id=user_id,
            movement_type=movement_type,
            quantity=applied_qty,
            previous_stock=historical_prev,
            new_stock=historical_new,
            reason=reason,
            notes=notes,
            product_name=product.name,
            product_code=product.product_code,
            presentation=product.presentation
        )
        return self._movement_repo.add(movement)

    def get_all_movements(self, limit: int = 100) -> List[InventoryMovement]:
        return self._movement_repo.get_all(limit=limit)

    def get_product_movements(self, product_id: int, limit: int = 50) -> List[InventoryMovement]:
        return self._movement_repo.get_by_product_id(product_id, limit=limit)

    def get_metrics(self) -> dict:
        return self._movement_repo.get_metrics()
