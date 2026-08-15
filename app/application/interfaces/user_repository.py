from abc import ABC, abstractmethod
from typing import Optional
from app.domain.models.user import User

class UserRepositoryInterface(ABC):
    @abstractmethod
    def add(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[User]:
        pass

    @abstractmethod
    def count_users(self) -> int:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass
