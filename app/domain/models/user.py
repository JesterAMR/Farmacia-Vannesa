from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    username: str
    password_hash: str
    role: str = 'cajero'
    id: Optional[int] = None
