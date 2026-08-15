from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AuditLog:
    action: str
    user_id: Optional[int] = None
    username: Optional[str] = None # Helper field
    details: Optional[str] = None
    timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id: Optional[int] = None
