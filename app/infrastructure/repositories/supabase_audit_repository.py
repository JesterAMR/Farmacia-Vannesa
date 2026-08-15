# app/infrastructure/repositories/supabase_audit_repository.py
from typing import List
from app.domain.models.audit_log import AuditLog
from app.infrastructure.database.supabase_connection import get_supabase_client

class SupabaseAuditRepository:
    def __init__(self):
        self.db = get_supabase_client()

    def create(self, log: AuditLog) -> AuditLog:
        data = {
            "action": log.action,
            "user_id": log.user_id,
            "username": log.username,
            "details": log.details,
            "timestamp": log.timestamp
        }
        response = self.db.table('audit_logs').insert(data).execute()
        if response.data:
            log.id = response.data[0].get('id')
        return log

    def get_recent(self, limit: int = 20) -> List[AuditLog]:
        # Supabase maneja los JOINs anidando el select con el nombre de la tabla referenciada: 'users(username)'
        response = self.db.table('audit_logs') \
            .select('*, users(username)') \
            .order('id', desc=True) \
            .limit(limit) \
            .execute()
        
        logs = []
        for row in response.data:
            # Extraemos el username del diccionario anidado 'users' que devuelve Supabase
            username_fetched = "Desconocido"
            if row.get('users'):
                username_fetched = row['users'].get('username', 'Desconocido')
                
            logs.append(AuditLog(
                id=row.get('id'),
                user_id=row.get('user_id'),
                username=username_fetched,
                action=row.get('action'),
                timestamp=row.get('timestamp'),
                details=row.get('details')
            ))
        return logs