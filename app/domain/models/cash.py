from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class CashShift:
    shift_name: str = "Matutino"
    register_name: str = "Caja #1 - Principal"
    initial_amount: float = 0.0
    user_id: Optional[int] = None
    cashier_username: Optional[str] = None
    expected_cash: Optional[float] = None
    physical_cash: Optional[float] = None
    difference: Optional[float] = None
    vault_deposit: Optional[float] = None
    remnant_cash: Optional[float] = None
    status: str = "Abierta" # 'Abierta', 'Cerrada'
    notes: Optional[str] = None
    opened_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    closed_at: Optional[str] = None
    id: Optional[int] = None

@dataclass
class CashMovement:
    movement_type: str # 'Ingreso', 'Egreso', 'Retiro Bóveda'
    concept: str
    amount: float
    category: str = "Operativo"
    voucher_reference: Optional[str] = None
    shift_id: Optional[int] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    id: Optional[int] = None
