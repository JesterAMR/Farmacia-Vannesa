from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.cash import CashShift, CashMovement

class CashRepositoryInterface(ABC):
    @abstractmethod
    def get_open_shift(self) -> Optional[CashShift]:
        pass

    @abstractmethod
    def open_shift(self, shift: CashShift) -> CashShift:
        pass

    @abstractmethod
    def close_shift(self, shift_id: int, physical_cash: float, expected_cash: float, 
                    difference: float, notes: Optional[str] = None) -> Optional[CashShift]:
        pass

    @abstractmethod
    def get_recent_shifts(self, limit: int = 10) -> List[CashShift]:
        pass

    @abstractmethod
    def add_movement(self, movement: CashMovement) -> CashMovement:
        pass

    @abstractmethod
    def get_movements(self, shift_id: Optional[int] = None, limit: int = 50) -> List[CashMovement]:
        pass

    @abstractmethod
    def get_financial_summary(self, shift_id: Optional[int] = None) -> dict:
        pass
