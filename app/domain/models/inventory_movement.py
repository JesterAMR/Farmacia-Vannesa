from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class InventoryMovement:
    product_id: int
    movement_type: str # 'Entrada', 'Salida', 'Ajuste / Merma'
    quantity: int
    reason: str
    previous_stock: int = 0
    new_stock: int = 0
    notes: Optional[str] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    presentation: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    id: Optional[int] = None

    @property
    def badge_class(self) -> str:
        t = (self.movement_type or "").lower()
        if "entrada" in t:
            return "badge-entry"
        elif "salida" in t:
            return "badge-exit"
        return "badge-adj"
