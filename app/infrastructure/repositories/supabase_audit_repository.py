# app/infrastructure/repositories/supabase_audit_repository.py
import os
import logging
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
        data = {
            "action": log.action,
            "user_id": log.user_id,
            "username": log.username,
            "details": log.details,
            "timestamp": log.timestamp
        }
        try:
            response = self.db.table('audit_logs').insert(data).execute()
            if response.data:
                log.id = response.data[0].get('id')
            return log
        except Exception as e:
            logging.error(f"[SupabaseAuditRepository] create error: {e}")
            return log

    def get_recent(self, limit: int = 20) -> List[AuditLog]:
        try:
            response = self.db.table('audit_logs') \
                .select('*, users(username)') \
                .order('id', desc=True) \
                .limit(limit) \
                .execute()
        except Exception as e:
            logging.warning(f"[SupabaseAuditRepository] Fallback without join: {e}")
            try:
                response = self.db.table('audit_logs') \
                    .select('*') \
                    .order('id', desc=True) \
                    .limit(limit) \
                    .execute()
            except Exception as e2:
                logging.error(f"[SupabaseAuditRepository] get_recent error: {e2}")
                return []

        logs = []
        for row in response.data or []:
            username_fetched = "Desconocido"
            if row.get('users'):
                username_fetched = row['users'].get('username', 'Desconocido')
            elif row.get('username'):
                username_fetched = row.get('username')
                
            logs.append(AuditLog(
                id=row.get('id'),
                user_id=row.get('user_id'),
                username=username_fetched,
                action=row.get('action', ''),
                timestamp=row.get('timestamp', ''),
                details=row.get('details', '')
            ))
        return logs
