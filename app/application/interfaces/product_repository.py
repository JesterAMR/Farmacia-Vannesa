from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.product import Product

class ProductRepositoryInterface(ABC):
    @abstractmethod
    def add(self, product: Product) -> Product:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Product]:
        pass

    @abstractmethod
    def get_all(self) -> List[Product]:
        pass

    @abstractmethod
    def update(self, product: Product) -> Product:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass
