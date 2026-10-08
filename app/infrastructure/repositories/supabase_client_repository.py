# app/infrastructure/repositories/supabase_client_repository.py
import os
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

    def get_paginated(self, page: int = 1, per_page: int = 10, search: Optional[str] = None):
        try:
            query = self.db.table('clients').select('*', count='exact')
            if search:
                s = search.strip()
                query = query.or_(f"name.ilike.%{s}%,identity_card.ilike.%{s}%,phone.ilike.%{s}%")
            start = (page - 1) * per_page
            end = start + per_page - 1
            response = query.range(start, end).execute()
            clients = []
            for row in response.data or []:
                clients.append(Client(
                    id=row.get('id'),
                    name=row.get('name', 'Consumidor Final'),
                    identity_card=row.get('identity_card', ''),
                    email=row.get('email'),
                    phone=row.get('phone')
                ))
            total = response.count if response.count is not None else len(clients)
            return clients, total
        except Exception as e:
            logging.warning(f"[SupabaseClientRepository] Fallback get_paginated: {e}")
            all_c = self.get_all()
            if search:
                s = search.lower().strip()
                all_c = [c for c in all_c if s in c.name.lower() or s in c.identity_card.lower() or (c.phone and s in c.phone.lower())]
            total = len(all_c)
            st = (page - 1) * per_page
            return all_c[st:st + per_page], total

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
