# check_supabase_tables.py
import sys
from app.infrastructure.database.supabase_connection import get_supabase_client

def check_all_tables():
    sb = get_supabase_client()
    tables = [
        "users",
        "products",
        "clients",
        "sales",
        "sale_items",
        "audit_logs",
        "cash_shifts",
        "cash_movements",
        "inventory_movements"
    ]
    
    print("=== Estado de las Tablas en Supabase ===")
    for t in tables:
        try:
            res = sb.table(t).select("*").limit(1).execute()
            print(f"[OK]        Tabla '{t}': EXISTE y LISTA")
        except Exception as e:
            code = getattr(e, 'code', 'PGRST205')
            print(f"[PENDIENTE] Tabla '{t}': NO EXISTE AUN EN SUPABASE")

if __name__ == "__main__":
    check_all_tables()
