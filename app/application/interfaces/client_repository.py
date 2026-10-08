from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
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

    def get_paginated(self, page: int = 1, per_page: int = 10, search: Optional[str] = None) -> Tuple[List[Client], int]:
        all_clients = self.get_all()
        if search:
            s = search.lower().strip()
            all_clients = [c for c in all_clients if s in c.name.lower() or s in c.identity_card.lower() or (c.phone and s in c.phone.lower())]
        total = len(all_clients)
        start = (page - 1) * per_page
        end = start + per_page
        return all_clients[start:end], total
