# app/infrastructure/repositories/supabase_user_repository.py
import logging
import os
from typing import List, Optional
from app.domain.models.user import User
from app.application.interfaces.user_repository import UserRepositoryInterface
from app.infrastructure.database.supabase_connection import get_supabase_client
from app.infrastructure.database.sqlite_connection import SQLiteDatabase
from app.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository

logger = logging.getLogger(__name__)

class SupabaseUserRepository(UserRepositoryInterface):
    def __init__(self):
        try:
            self.db = get_supabase_client()
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase client: {e}")
            self.db = None
            
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(base_dir, 'vannesa_db.sqlite')
        self._sqlite_repo = SQLiteUserRepository(SQLiteDatabase(db_path=db_path))

    def count_users(self) -> int:
        if self.db:
            try:
                response = self.db.table('users').select('id', count='exact').execute()
                return response.count if response.count is not None else 0
            except Exception as e:
                logger.warning(f"Supabase error in count_users: {e}. Falling back to SQLite.")
        return self._sqlite_repo.count_users()

    def get_all(self) -> List[User]:
        if self.db:
            try:
                response = self.db.table('users').select('*').execute()
                return [
                    User(
                        id=row.get('id'),
                        username=row.get('username'),
                        password_hash=row.get('password_hash'),
                        role=row.get('role', 'cajero')
                    ) for row in response.data
                ]
            except Exception as e:
                logger.warning(f"Supabase error in get_all users: {e}. Falling back to SQLite.")
        return self._sqlite_repo.get_all()

    def get_by_id(self, user_id: int) -> Optional[User]:
        if self.db:
            try:
                response = self.db.table('users').select('*').eq('id', user_id).execute()
                if response.data:
                    row = response.data[0]
                    return User(
                        id=row.get('id'),
                        username=row.get('username'),
                        password_hash=row.get('password_hash'),
                        role=row.get('role', 'cajero')
                    )
                return None
            except Exception as e:
                logger.warning(f"Supabase error in get_by_id user: {e}. Falling back to SQLite.")
        return self._sqlite_repo.get_by_id(user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        if self.db:
            try:
                response = self.db.table('users').select('*').eq('username', username).execute()
                if response.data:
                    row = response.data[0]
                    return User(
                        id=row.get('id'),
                        username=row.get('username'),
                        password_hash=row.get('password_hash'),
                        role=row.get('role', 'cajero')
                    )
                return None
            except Exception as e:
                logger.warning(f"Supabase error in get_by_username: {e}. Falling back to SQLite.")
        return self._sqlite_repo.get_by_username(username)

    def add(self, user: User) -> User:
        if self.db:
            try:
                data = {
                    "username": user.username,
                    "password_hash": user.password_hash,
                    "role": user.role
                }
                if user.id is not None:
                    data["id"] = user.id
                response = self.db.table('users').insert(data).execute()
                if response.data:
                    user.id = response.data[0].get('id')
                return user
            except Exception as e:
                logger.warning(f"Supabase error in add user: {e}. Falling back to SQLite.")
        return self._sqlite_repo.add(user)

    def update(self, user: User) -> User:
        if self.db:
            try:
                data = {
                    "username": user.username,
                    "password_hash": user.password_hash,
                    "role": user.role
                }
                self.db.table('users').update(data).eq('id', user.id).execute()
                return user
            except Exception as e:
                logger.warning(f"Supabase error in update user: {e}. Falling back to SQLite.")
        return self._sqlite_repo.update(user)

    def delete(self, user_id: int) -> bool:
        if self.db:
            try:
                response = self.db.table('users').delete().eq('id', user_id).execute()
                return len(response.data) > 0
            except Exception as e:
                logger.warning(f"Supabase error in delete user: {e}. Falling back to SQLite.")
        return self._sqlite_repo.delete(user_id)