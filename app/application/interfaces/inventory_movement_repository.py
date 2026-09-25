from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.inventory_movement import InventoryMovement

class InventoryMovementRepositoryInterface(ABC):
    @abstractmethod
    def add(self, movement: InventoryMovement) -> InventoryMovement:
        pass

    @abstractmethod
    def get_all(self, limit: int = 100) -> List[InventoryMovement]:
        pass

    @abstractmethod
    def get_by_product_id(self, product_id: int, limit: int = 50) -> List[InventoryMovement]:
        pass

    @abstractmethod
    def get_metrics(self) -> dict:
        pass
