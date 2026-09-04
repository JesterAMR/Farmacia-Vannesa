# app/infrastructure/repositories/supabase_client_repository.py
import logging
import os
from typing import List, Optional
from app.domain.models.client import Client
from app.application.interfaces.client_repository import ClientRepositoryInterface
from app.infrastructure.database.supabase_connection import get_supabase_client
from app.infrastructure.database.sqlite_connection import SQLiteDatabase
from app.infrastructure.repositories.sqlite_client_repository import SQLiteClientRepository

logger = logging.getLogger(__name__)

class SupabaseClientRepository(ClientRepositoryInterface):
    def __init__(self):
        try:
            self.db = get_supabase_client()
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase client: {e}")
            self.db = None
            
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(base_dir, 'vannesa_db.sqlite')
        self._sqlite_repo = SQLiteClientRepository(SQLiteDatabase(db_path=db_path))

    def get_all(self) -> List[Client]:
        if self.db:
            try:
                response = self.db.table('clients').select('*').execute()
                clients = []
                for row in response.data:
                    clients.append(Client(
                        id=row.get('id'),
                        name=row.get('name'),
                        identity_card=row.get('identity_card'),
                        email=row.get('email'),
                        phone=row.get('phone')
                    ))
                return clients
            except Exception as e:
                logger.warning(f"Supabase error in get_all clients: {e}. Falling back to SQLite.")
        return self._sqlite_repo.get_all()

    def get_by_id(self, client_id: int) -> Optional[Client]:
        if self.db:
            try:
                response = self.db.table('clients').select('*').eq('id', client_id).execute()
                if not response.data:
                    return None
                row = response.data[0]
                return Client(
                    id=row.get('id'),
                    name=row.get('name'),
                    identity_card=row.get('identity_card'),
                    email=row.get('email'),
                    phone=row.get('phone')
                )
            except Exception as e:
                logger.warning(f"Supabase error in get_by_id client: {e}. Falling back to SQLite.")
        return self._sqlite_repo.get_by_id(client_id)

    def get_by_identity_card(self, identity_card: str) -> Optional[Client]:
        if self.db:
            try:
                response = self.db.table('clients').select('*').eq('identity_card', identity_card).execute()
                if not response.data:
                    return None
                row = response.data[0]
                return Client(
                    id=row.get('id'),
                    name=row.get('name'),
                    identity_card=row.get('identity_card'),
                    email=row.get('email'),
                    phone=row.get('phone')
                )
            except Exception as e:
                logger.warning(f"Supabase error in get_by_identity_card: {e}. Falling back to SQLite.")
        return self._sqlite_repo.get_by_identity_card(identity_card)

    def add(self, client: Client) -> Client:
        if self.db:
            try:
                data = {
                    "name": client.name,
                    "identity_card": client.identity_card,
                    "email": client.email,
                    "phone": client.phone
                }
                if client.id is not None:
                    data["id"] = client.id
                    
                response = self.db.table('clients').insert(data).execute()
                if response.data:
                    client.id = response.data[0].get('id')
                return client
            except Exception as e:
                logger.warning(f"Supabase error in add client: {e}. Falling back to SQLite.")
        return self._sqlite_repo.add(client)

    def update(self, client: Client) -> Client:
        if self.db:
            try:
                data = {
                    "name": client.name,
                    "identity_card": client.identity_card,
                    "email": client.email,
                    "phone": client.phone
                }
                self.db.table('clients').update(data).eq('id', client.id).execute()
                return client
            except Exception as e:
                logger.warning(f"Supabase error in update client: {e}. Falling back to SQLite.")
        return self._sqlite_repo.update(client)

    def delete(self, client_id: int) -> bool:
        if self.db:
            try:
                response = self.db.table('clients').delete().eq('id', client_id).execute()
                return len(response.data) > 0
            except Exception as e:
                logger.warning(f"Supabase error in delete client: {e}. Falling back to SQLite.")
        return self._sqlite_repo.delete(client_id)