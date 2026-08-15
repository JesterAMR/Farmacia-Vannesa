from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from app.domain.models.user import User
from app.application.interfaces.user_repository import UserRepositoryInterface

class AuthService:
    def __init__(self, user_repository: UserRepositoryInterface):
        self._user_repository = user_repository

    def register(self, username: str, password: str, role: Optional[str] = None) -> bool:
        if self._user_repository.get_by_username(username):
            return False  # El username ya existe
            
        # Determinar rol por defecto
        if not role:
            if self._user_repository.count_users() == 0:
                role = 'admin'
            else:
                role = 'cajero'

        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash, role=role)
        self._user_repository.add(new_user)
        return True

    def login(self, username: str, password: str) -> Optional[User]:
        user = self._user_repository.get_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            return user
        return None

    def get_user_by_id(self, id: int) -> Optional[User]:
        return self._user_repository.get_by_id(id)

    def change_password(self, user_id: int, new_password: str) -> bool:
        user = self._user_repository.get_by_id(user_id)
        if not user:
            return False
        user.password_hash = generate_password_hash(new_password)
        self._user_repository.update(user)
        return True
