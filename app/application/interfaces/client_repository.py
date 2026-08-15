from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.client import Client

class ClientRepositoryInterface(ABC):
    @abstractmethod
    def add(self, client: Client) -> Client:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Client]:
        pass

    @abstractmethod
    def get_by_identity_card(self, identity_card: str) -> Optional[Client]:
        pass

    @abstractmethod
    def get_all(self) -> List[Client]:
        pass

    @abstractmethod
    def update(self, client: Client) -> Client:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass
