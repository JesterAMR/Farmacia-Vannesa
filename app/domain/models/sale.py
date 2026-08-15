from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class SaleItem:
    product_id: int
    quantity: int
    price: float  # Price at the time of sale
    subtotal: float
    id: Optional[int] = None
    sale_id: Optional[int] = None

@dataclass
class Sale:
    total: float
    items: List[SaleItem] = field(default_factory=list)
    date: str = field(default_factory=lambda: datetime.now().isoformat())
    client_id: Optional[int] = None
    id: Optional[int] = None
