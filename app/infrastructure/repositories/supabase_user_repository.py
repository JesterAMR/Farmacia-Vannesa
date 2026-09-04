# app/infrastructure/repositories/supabase_user_repository.py
import logging
from typing import List, Optional
from app.domain.models.user import User
from app.application.interfaces.user_repository import UserRepositoryInterface
from app.infrastructure.database.supabase_connection import get_supabase_client

class SupabaseUserRepository(UserRepositoryInterface):
    def __init__(self):
        self.db = get_supabase_client()

    def count_users(self) -> int:
        try:
            response = self.db.table('users').select('id', count='exact').execute()
            return response.count if response.count is not None else 0
        except Exception as e:
            logging.error(f"[SupabaseUserRepository] count_users error: {e}")
            return 0

    def get_all(self) -> List[User]:
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
            logging.error(f"[SupabaseUserRepository] get_all error: {e}")
            return []

    def get_by_id(self, user_id: int) -> Optional[User]:
        try:
            response = self.db.table('users').select('*').eq('id', user_id).execute()
            if not response.data:
                return None
            row = response.data[0]
            return User(
                id=row.get('id'),
                username=row.get('username'),
                password_hash=row.get('password_hash'),
                role=row.get('role', 'cajero')
            )
        except Exception as e:
            logging.error(f"[SupabaseUserRepository] get_by_id error: {e}")
            return None

    def get_by_username(self, username: str) -> Optional[User]:
        try:
            response = self.db.table('users').select('*').eq('username', username).execute()
            if not response.data:
                return None
            row = response.data[0]
            return User(
                id=row.get('id'),
                username=row.get('username'),
                password_hash=row.get('password_hash'),
                role=row.get('role', 'cajero')
            )
        except Exception as e:
            logging.error(f"[SupabaseUserRepository] get_by_username error: {e}")
            raise e

    def add(self, user: User) -> User:
        data = {
            "username": user.username,
            "password_hash": user.password_hash,
            "role": user.role
        }
        if user.id is not None:
            data["id"] = user.id
            
        try:
            response = self.db.table('users').insert(data).execute()
            if response.data:
                user.id = response.data[0].get('id')
            return user
        except Exception as e:
            logging.error(f"[SupabaseUserRepository] add error: {e}")
            raise e

    def update(self, user: User) -> User:
        data = {
            "username": user.username,
            "password_hash": user.password_hash,
            "role": user.role
        }
        try:
            self.db.table('users').update(data).eq('id', user.id).execute()
            return user
        except Exception as e:
            logging.error(f"[SupabaseUserRepository] update error: {e}")
            raise e

    def delete(self, user_id: int) -> bool:
        try:
            response = self.db.table('users').delete().eq('id', user_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logging.error(f"[SupabaseUserRepository] delete error: {e}")
            return False
