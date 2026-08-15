from typing import List, Optional
from app.domain.models.client import Client
from app.application.interfaces.client_repository import ClientRepositoryInterface

class ClientService:
    def __init__(self, client_repository: ClientRepositoryInterface):
        self._client_repository = client_repository

    def create_client(self, name: str, identity_card: str, email: Optional[str] = None, phone: Optional[str] = None) -> Client:
        if not name or not identity_card:
            raise ValueError("El nombre y la identificación son requeridos.")
            
        existing = self._client_repository.get_by_identity_card(identity_card)
        if existing:
            raise ValueError("Ya existe un cliente con esta identificación.")
            
        client = Client(name=name, identity_card=identity_card, email=email, phone=phone)
        return self._client_repository.add(client)

    def get_client(self, id: int) -> Optional[Client]:
        return self._client_repository.get_by_id(id)

    def get_client_by_identity(self, identity_card: str) -> Optional[Client]:
        return self._client_repository.get_by_identity_card(identity_card)

    def get_all_clients(self) -> List[Client]:
        return self._client_repository.get_all()

    def update_client(self, id: int, name: str, identity_card: str, email: Optional[str] = None, phone: Optional[str] = None) -> Client:
        client = self._client_repository.get_by_id(id)
        if not client:
            raise ValueError("Cliente no encontrado.")
            
        # Check if identification is being changed to an existing one
        if identity_card != client.identity_card:
            existing = self._client_repository.get_by_identity_card(identity_card)
            if existing:
                raise ValueError("Ya existe otro cliente con esta identificación.")
                
        client.name = name
        client.identity_card = identity_card
        client.email = email
        client.phone = phone
        
        return self._client_repository.update(client)

    def delete_client(self, id: int) -> bool:
        return self._client_repository.delete(id)
