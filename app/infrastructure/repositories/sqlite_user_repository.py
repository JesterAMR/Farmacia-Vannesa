import sqlite3
from typing import List, Optional
from app.domain.models.user import User
from app.application.interfaces.user_repository import UserRepositoryInterface
from app.infrastructure.database.sqlite_connection import SQLiteDatabase

class SQLiteUserRepository(UserRepositoryInterface):
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def add(self, user: User) -> User:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (user.username, user.password_hash, user.role)
            )
            conn.commit()
            user.id = cursor.lastrowid
            return user

    def get_by_username(self, username: str) -> Optional[User]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return User(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    role=row['role']
                )
            return None

    def get_by_id(self, id: int) -> Optional[User]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
            row = cursor.fetchone()
            if row:
                return User(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    role=row['role']
                )
            return None

    def count_users(self) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]

    def get_all(self) -> List[User]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            return [
                User(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    role=row['role']
                ) for row in rows
            ]

    def update(self, user: User) -> User:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET username = ?, password_hash = ?, role = ? WHERE id = ?",
                (user.username, user.password_hash, user.role, user.id)
            )
            conn.commit()
            return user

    def delete(self, id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
