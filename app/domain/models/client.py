from dataclasses import dataclass
from typing import Optional

@dataclass
class Client:
    name: str
    identity_card: str # Cédula, RUC, o NIT
    email: Optional[str] = None
    phone: Optional[str] = None
    id: Optional[int] = None
