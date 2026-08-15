# app/infrastructure/database/supabase_connection.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carga las variables del archivo .env
load_dotenv()

# Lee las variables reales o lanza un error si no las encuentra
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Faltan las credenciales de Supabase. Revisa tu archivo .env")

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)