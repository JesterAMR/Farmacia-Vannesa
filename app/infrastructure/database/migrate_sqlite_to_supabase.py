# app/infrastructure/database/migrate_sqlite_to_supabase.py
import sqlite3
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from app.infrastructure.database.supabase_connection import get_supabase_client

def migrate():
    # Detect SQLite path
    sqlite_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "vannesa_db.sqlite"))
    if not os.path.exists(sqlite_path):
        sqlite_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "vannesa_db.sqlite"))
        
    print(f"SQLite Database Path: {sqlite_path}")
    if not os.path.exists(sqlite_path):
        print("ERROR: SQLite database file not found!")
        return

    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    # Connect to Supabase
    try:
        supabase = get_supabase_client()
        print("Supabase client initialized successfully.")
    except Exception as e:
        print(f"ERROR connecting to Supabase: {e}")
        return

    # Step 1: Clean existing data in Supabase (reverse dependency order)
    tables_to_clean = ["audit_logs", "sale_items", "sales", "clients", "products", "users"]
    print("\n--- Cleaning existing data in Supabase ---")
    for table in tables_to_clean:
        try:
            print(f"Cleaning table '{table}'...")
            supabase.table(table).delete().neq("id", -1).execute()
        except Exception as e:
            print(f"Warning cleaning '{table}': {e} (It might be empty or not exists yet)")

    # Step 2: Migrate in dependency order
    # Helper to migrate a table
    def migrate_table(table_name, sqlite_query, map_row_fn):
        print(f"\n--- Migrating table '{table_name}' ---")
        sqlite_cursor.execute(sqlite_query)
        rows = sqlite_cursor.fetchall()
        print(f"Found {len(rows)} rows in SQLite.")
        
        if not rows:
            print("No data to migrate.")
            return

        batch = []
        batch_size = 50
        for i, row in enumerate(rows):
            batch.append(map_row_fn(dict(row)))
            if len(batch) == batch_size or i == len(rows) - 1:
                try:
                    supabase.table(table_name).insert(batch).execute()
                    print(f"Uploaded batch of {len(batch)} rows (Progress: {i+1}/{len(rows)})")
                except Exception as e:
                    print(f"ERROR uploading batch to '{table_name}': {e}")
                    print("Sample payload of failed batch:", batch[0] if batch else None)
                    raise e
                batch = []

    # Map functions
    def map_user(row):
        return {
            "id": row["id"],
            "username": row["username"],
            "password_hash": row["password_hash"],
            "role": row["role"]
        }

    def map_product(row):
        return {
            "id": row["id"],
            "name": row["name"],
            "generic_name": row["generic_name"],
            "product_code": row["product_code"],
            "description": row["description"],
            "stock": row["stock"],
            "presentation": row["presentation"],
            "laboratory": row["laboratory"],
            "expiration_date": row["expiration_date"],
            "dose": row["dose"],
            "cost_price": row["cost_price"],
            "sale_price": row["sale_price"]
        }

    def map_client(row):
        return {
            "id": row["id"],
            "name": row["name"],
            "identity_card": row["identity_card"],
            "email": row["email"],
            "phone": row["phone"]
        }

    def map_sale(row):
        return {
            "id": row["id"],
            "total": row["total"],
            "date": row["date"],
            "client_id": row["client_id"]
        }

    def map_sale_item(row):
        return {
            "id": row["id"],
            "sale_id": row["sale_id"],
            "product_id": row["product_id"],
            "quantity": row["quantity"],
            "price": row["price"],
            "subtotal": row["subtotal"]
        }

    def map_audit_log(row):
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "action": row["action"],
            "timestamp": row["timestamp"],
            "details": row["details"]
        }

    # Execute migrations
    try:
        # Migrate users
        migrate_table("users", "SELECT * FROM users", map_user)
        
        # Migrate products and check for orphan/missing product IDs referenced in sale_items
        sqlite_cursor.execute("SELECT id FROM products")
        existing_product_ids = {r[0] for r in sqlite_cursor.fetchall()}
        
        sqlite_cursor.execute("SELECT DISTINCT product_id FROM sale_items")
        referenced_product_ids = {r[0] for r in sqlite_cursor.fetchall()}
        
        missing_product_ids = referenced_product_ids - existing_product_ids
        
        # Migrate actual products
        migrate_table("products", "SELECT * FROM products", map_product)
        
        # Insert placeholders for missing products to satisfy FK constraints
        if missing_product_ids:
            print(f"\n--- Found {len(missing_product_ids)} missing products referenced in sale_items. Inserting placeholders. ---")
            placeholders = []
            for pid in missing_product_ids:
                print(f"Creating placeholder product for ID: {pid}")
                placeholders.append({
                    "id": pid,
                    "name": f"Producto No Disponible (ID: {pid})",
                    "generic_name": "No Disponible",
                    "product_code": f"DESCONOCIDO_{pid}",
                    "description": "Producto huérfano recuperado de ventas históricas.",
                    "stock": 0,
                    "presentation": "N/A",
                    "laboratory": "N/A",
                    "expiration_date": "2030-01-01",
                    "dose": "N/A",
                    "cost_price": 0.0,
                    "sale_price": 0.0
                })
            supabase.table("products").insert(placeholders).execute()
            print("Successfully inserted placeholder products.")

        migrate_table("clients", "SELECT * FROM clients", map_client)
        migrate_table("sales", "SELECT * FROM sales", map_sale)
        migrate_table("sale_items", "SELECT * FROM sale_items", map_sale_item)
        migrate_table("audit_logs", "SELECT * FROM audit_logs", map_audit_log)
        
        print("\n==============================================")
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("==============================================")
    except Exception as e:
        print(f"\nMigration failed with error: {e}")
    finally:
        sqlite_conn.close()

if __name__ == '__main__':
    migrate()
