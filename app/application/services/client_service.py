import math
from typing import List, Optional, Dict, Any
from app.domain.models.client import Client
from app.application.interfaces.client_repository import ClientRepositoryInterface

class ClientService:
    def __init__(self, client_repository: ClientRepositoryInterface):
        self._client_repository = client_repository

    def create_client(self, name: str, identity_card: str, email: Optional[str] = None, phone: Optional[str] = None) -> Client:
        if not name or not identity_card:
            raise ValueError("El nombre y la identificación (Cédula o RUC) son requeridos.")
            
        existing = self._client_repository.get_by_identity_card(identity_card.strip())
        if existing:
            raise ValueError("Ya existe un cliente con esta identificación fiscal.")
            
        client = Client(name=name.strip(), identity_card=identity_card.strip(), email=email, phone=phone)
        return self._client_repository.add(client)

    def get_client(self, id: int) -> Optional[Client]:
        return self._client_repository.get_by_id(id)

    def get_client_by_identity(self, identity_card: str) -> Optional[Client]:
        return self._client_repository.get_by_identity_card(identity_card)

    def get_all_clients(self) -> List[Client]:
        return self._client_repository.get_all()

    def get_paginated_clients(self, page: int = 1, per_page: int = 10, search: Optional[str] = None) -> Dict[str, Any]:
        page = max(1, int(page))
        per_page = max(1, min(100, int(per_page)))
        items, total = self._client_repository.get_paginated(page=page, per_page=per_page, search=search)
        total_pages = max(1, math.ceil(total / per_page))
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages,
            "prev_page": page - 1 if page > 1 else None,
            "next_page": page + 1 if page < total_pages else None
        }

    def update_client(self, id: int, name: str, identity_card: str, email: Optional[str] = None, phone: Optional[str] = None) -> Client:
        client = self._client_repository.get_by_id(id)
        if not client:
            raise ValueError("Cliente no encontrado.")
            
        if identity_card.strip() != client.identity_card:
            existing = self._client_repository.get_by_identity_card(identity_card.strip())
            if existing:
                raise ValueError("Ya existe otro cliente con esta identificación.")
                
        client.name = name.strip()
        client.identity_card = identity_card.strip()
        client.email = email
        client.phone = phone
        
        return self._client_repository.update(client)

    def delete_client(self, id: int) -> bool:
        return self._client_repository.delete(id)
