# app/application/services/audit_service.py
from typing import List
from app.domain.models.audit_log import AuditLog

class AuditService:
    # Ahora recibimos el repositorio en lugar de la conexión a la base de datos
    def __init__(self, audit_repository):
        self.audit_repo = audit_repository

    def log_action(self, action: str, user_id: int, details: str = None) -> AuditLog:
        # Creamos el objeto de dominio
        log = AuditLog(action=action, user_id=user_id, details=details)
        
        # Delegamos la creación al repositorio
        return self.audit_repo.create(log)

    def get_recent_logs(self, limit: int = 20) -> List[AuditLog]:
        # Delegamos la consulta (con su límite y join) al repositorio
        return self.audit_repo.get_recent(limit)