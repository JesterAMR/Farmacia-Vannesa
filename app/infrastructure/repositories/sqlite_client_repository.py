import sqlite3
from typing import List, Optional
from app.domain.models.client import Client
from app.application.interfaces.client_repository import ClientRepositoryInterface
from app.infrastructure.database.sqlite_connection import SQLiteDatabase

class SQLiteClientRepository(ClientRepositoryInterface):
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def _row_to_client(self, row) -> Client:
        return Client(
            id=row['id'],
            name=row['name'],
            identity_card=row['identity_card'],
            email=row['email'],
            phone=row['phone']
        )

    def add(self, client: Client) -> Client:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO clients (name, identity_card, email, phone) 
                   VALUES (?, ?, ?, ?)""",
                (client.name, client.identity_card, client.email, client.phone)
            )
            conn.commit()
            client.id = cursor.lastrowid
            return client

    def get_by_id(self, id: int) -> Optional[Client]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients WHERE id = ?", (id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_client(row)
            return None

    def get_by_identity_card(self, identity_card: str) -> Optional[Client]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients WHERE identity_card = ?", (identity_card,))
            row = cursor.fetchone()
            if row:
                return self._row_to_client(row)
            return None

    def get_all(self) -> List[Client]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients ORDER BY name ASC")
            rows = cursor.fetchall()
            return [self._row_to_client(row) for row in rows]

    def update(self, client: Client) -> Client:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE clients SET name = ?, identity_card = ?, email = ?, phone = ? 
                   WHERE id = ?""",
                (client.name, client.identity_card, client.email, client.phone, client.id)
            )
            conn.commit()
            return client

    def delete(self, id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
