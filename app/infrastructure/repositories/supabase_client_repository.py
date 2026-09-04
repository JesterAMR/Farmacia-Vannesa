# app/infrastructure/repositories/supabase_client_repository.py
import logging
from typing import List, Optional
from app.domain.models.client import Client
from app.application.interfaces.client_repository import ClientRepositoryInterface
from app.infrastructure.database.supabase_connection import get_supabase_client

class SupabaseClientRepository(ClientRepositoryInterface):
    def __init__(self):
        self.db = get_supabase_client()

    def get_all(self) -> List[Client]:
        try:
            response = self.db.table('clients').select('*').execute()
            clients = []
            for row in response.data or []:
                clients.append(Client(
                    id=row.get('id'),
                    name=row.get('name', 'Consumidor Final'),
                    identity_card=row.get('identity_card', ''),
                    email=row.get('email'),
                    phone=row.get('phone')
                ))
            return clients
        except Exception as e:
            logging.error(f"[SupabaseClientRepository] get_all error: {e}")
            return []

    def get_by_id(self, client_id: int) -> Optional[Client]:
        try:
            response = self.db.table('clients').select('*').eq('id', client_id).execute()
            if not response.data:
                return None
            row = response.data[0]
            return Client(
                id=row.get('id'),
                name=row.get('name', 'Consumidor Final'),
                identity_card=row.get('identity_card', ''),
                email=row.get('email'),
                phone=row.get('phone')
            )
        except Exception as e:
            logging.error(f"[SupabaseClientRepository] get_by_id ({client_id}) error: {e}")
            return None

    def get_by_identity_card(self, identity_card: str) -> Optional[Client]:
        try:
            response = self.db.table('clients').select('*').eq('identity_card', identity_card).execute()
            if not response.data:
                return None
            row = response.data[0]
            return Client(
                id=row.get('id'),
                name=row.get('name', 'Consumidor Final'),
                identity_card=row.get('identity_card', ''),
                email=row.get('email'),
                phone=row.get('phone')
            )
        except Exception as e:
            logging.error(f"[SupabaseClientRepository] get_by_identity_card error: {e}")
            return None

    def add(self, client: Client) -> Client:
        data = {
            "name": client.name,
            "identity_card": client.identity_card,
            "email": client.email,
            "phone": client.phone
        }
        if client.id is not None:
            data["id"] = client.id
            
        try:
            response = self.db.table('clients').insert(data).execute()
            if response.data:
                client.id = response.data[0].get('id')
            return client
        except Exception as e:
            logging.error(f"[SupabaseClientRepository] add error: {e}")
            raise e

    def update(self, client: Client) -> Client:
        data = {
            "name": client.name,
            "identity_card": client.identity_card,
            "email": client.email,
            "phone": client.phone
        }
        try:
            self.db.table('clients').update(data).eq('id', client.id).execute()
            return client
        except Exception as e:
            logging.error(f"[SupabaseClientRepository] update error: {e}")
            raise e

    def delete(self, client_id: int) -> bool:
        try:
            response = self.db.table('clients').delete().eq('id', client_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logging.error(f"[SupabaseClientRepository] delete error: {e}")
            return False