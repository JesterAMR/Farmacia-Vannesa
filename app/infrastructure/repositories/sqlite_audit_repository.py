import sqlite3
from typing import List
from app.domain.models.audit_log import AuditLog
from app.infrastructure.database.sqlite_connection import SQLiteDatabase

class SQLiteAuditRepository:
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def create(self, log: AuditLog) -> AuditLog:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO audit_logs (user_id, action, timestamp, details) 
                   VALUES (?, ?, ?, ?)""",
                (log.user_id, log.action, log.timestamp, log.details)
            )
            conn.commit()
            log.id = cursor.lastrowid
            return log

    def get_recent(self, limit: int = 20) -> List[AuditLog]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.id, a.user_id, a.action, a.timestamp, a.details, u.username 
                FROM audit_logs a 
                LEFT JOIN users u ON a.user_id = u.id 
                ORDER BY a.id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            logs = []
            for row in rows:
                logs.append(AuditLog(
                    id=row['id'],
                    user_id=row['user_id'],
                    username=row['username'] if row['username'] else "Desconocido",
                    action=row['action'],
                    timestamp=row['timestamp'],
                    details=row['details']
                ))
            return logs
