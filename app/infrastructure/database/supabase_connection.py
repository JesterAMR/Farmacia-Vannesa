# app/infrastructure/database/supabase_connection.py
import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

# Carga variables locales de .env si existe (entorno local)
load_dotenv()

# Lee las variables de entorno (útil para Render, Heroku o local)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()

_supabase_client_instance = None

def get_supabase_client() -> Client:
    global _supabase_client_instance
    if _supabase_client_instance is not None:
        return _supabase_client_instance

    url = os.environ.get("SUPABASE_URL", SUPABASE_URL).strip()
    key = os.environ.get("SUPABASE_KEY", SUPABASE_KEY).strip()

    if not url or not key:
        error_msg = (
            "ERROR CRÍTICO: Faltan las variables de entorno 'SUPABASE_URL' y/o 'SUPABASE_KEY'. "
            "En Render, ve a tu panel: Dashboard -> Tu Servicio -> Environment -> 'Add Environment Variable' "
            "y agrega SUPABASE_URL y SUPABASE_KEY con la clave JWT (anon o service_role) de Supabase."
        )
        logging.critical(error_msg)
        raise ValueError(error_msg)

    try:
        _supabase_client_instance = create_client(url, key)
        return _supabase_client_instance
    except Exception as e:
        logging.critical(f"Error inicializando cliente de Supabase ({url}): {e}")
        raise e