# app/infrastructure/repositories/supabase_audit_repository.py
import logging
import os
from typing import List
from app.domain.models.audit_log import AuditLog
from app.infrastructure.database.supabase_connection import get_supabase_client
from app.infrastructure.database.sqlite_connection import SQLiteDatabase
from app.infrastructure.repositories.sqlite_audit_repository import SQLiteAuditRepository

logger = logging.getLogger(__name__)

class SupabaseAuditRepository:
    def __init__(self):
        try:
            self.db = get_supabase_client()
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase client: {e}")
            self.db = None
            
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(base_dir, 'vannesa_db.sqlite')
        self._sqlite_repo = SQLiteAuditRepository(SQLiteDatabase(db_path=db_path))

    def create(self, log: AuditLog) -> AuditLog:
        if self.db:
            try:
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
            except Exception as e:
                logger.warning(f"Supabase error in create audit log: {e}. Falling back to SQLite.")
        return self._sqlite_repo.create(log)

    def get_recent(self, limit: int = 20) -> List[AuditLog]:
        if self.db:
            try:
                response = self.db.table('audit_logs') \
                    .select('*, users(username)') \
                    .order('id', desc=True) \
                    .limit(limit) \
                    .execute()
                
                logs = []
                for row in response.data:
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
            except Exception as e:
                logger.warning(f"Supabase error in get_recent audit logs: {e}. Falling back to SQLite.")
        return self._sqlite_repo.get_recent(limit=limit)