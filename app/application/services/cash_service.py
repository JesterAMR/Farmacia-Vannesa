from typing import List, Optional
from app.domain.models.cash import CashShift, CashMovement
from app.application.interfaces.cash_repository import CashRepositoryInterface

class CashService:
    def __init__(self, cash_repository: CashRepositoryInterface):
        self._cash_repo = cash_repository

    def get_open_shift(self) -> Optional[CashShift]:
        return self._cash_repo.get_open_shift()

    def open_shift(self, cashier: str, shift_name: str, initial_amount: float, 
                   notes: Optional[str] = None, user_id: Optional[int] = None) -> CashShift:
        # Verify if there is already an open shift
        current_open = self.get_open_shift()
        if current_open:
            raise ValueError(f"Ya existe un turno abierto (#{current_open.id} - {current_open.shift_name}). Debe cerrarlo antes de iniciar una nueva apertura.")

        shift = CashShift(
            shift_name=shift_name,
            register_name="Caja #1 - Principal",
            initial_amount=initial_amount,
            user_id=user_id,
            cashier_username=cashier,
            notes=notes
        )
        return self._cash_repo.open_shift(shift)

    def close_shift(self, physical_cash: float, notes: Optional[str] = None) -> CashShift:
        current_open = self.get_open_shift()
        if not current_open:
            raise ValueError("No hay ningún turno de caja abierto para realizar el arqueo y cierre.")

        summary = self._cash_repo.get_financial_summary(shift_id=current_open.id)
        expected_cash = summary["current_drawer"]
        diff = round(physical_cash - expected_cash, 2)

        return self._cash_repo.close_shift(
            shift_id=current_open.id,
            physical_cash=physical_cash,
            expected_cash=expected_cash,
            difference=diff,
            notes=notes
        )

    def add_movement(self, movement_type: str, concept: str, amount: float, 
                     category: str = "Operativo", voucher: Optional[str] = None, 
                     user_id: Optional[int] = None) -> CashMovement:
        if amount <= 0:
            raise ValueError("El monto del movimiento debe ser superior a cero.")

        current_open = self.get_open_shift()
        shift_id = current_open.id if current_open else None

        movement = CashMovement(
            shift_id=shift_id,
            user_id=user_id,
            movement_type=movement_type,
            category=category,
            concept=concept,
            amount=amount,
            voucher_reference=voucher
        )
        return self._cash_repo.add_movement(movement)

    def get_recent_shifts(self, limit: int = 10) -> List[CashShift]:
        return self._cash_repo.get_recent_shifts(limit)

    def get_movements(self, shift_id: Optional[int] = None, limit: int = 50) -> List[CashMovement]:
        return self._cash_repo.get_movements(shift_id=shift_id, limit=limit)

    def get_financial_summary(self, shift_id: Optional[int] = None) -> dict:
        return self._cash_repo.get_financial_summary(shift_id=shift_id)
