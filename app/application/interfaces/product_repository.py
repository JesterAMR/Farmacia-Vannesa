from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from app.domain.models.product import Product

class ProductRepositoryInterface(ABC):
    @abstractmethod
    def add(self, product: Product) -> Product:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Product]:
        pass

    @abstractmethod
    def get_by_code(self, product_code: str) -> Optional[Product]:
        pass

    @abstractmethod
    def get_all(self, include_inactive: bool = False) -> List[Product]:
        pass

    @abstractmethod
    def update(self, product: Product) -> Product:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass

    def get_paginated(self, page: int = 1, per_page: int = 10, search: Optional[str] = None, include_inactive: bool = False) -> Tuple[List[Product], int]:
        """Retorna una tupla (lista_de_productos_de_la_pagina, total_registros)."""
        all_prods = self.get_all(include_inactive=include_inactive)
        if search:
            s = search.lower().strip()
            all_prods = [p for p in all_prods if s in p.name.lower() or s in p.generic_name.lower() or s in p.product_code.lower()]
        total = len(all_prods)
        start = (page - 1) * per_page
        end = start + per_page
        return all_prods[start:end], total
