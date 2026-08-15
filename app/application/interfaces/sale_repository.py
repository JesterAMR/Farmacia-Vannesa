from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.sale import Sale

class SaleRepositoryInterface(ABC):
    @abstractmethod
    def add(self, sale: Sale) -> Sale:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Sale]:
        pass

    @abstractmethod
    def get_all(self) -> List[Sale]:
        pass
