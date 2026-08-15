import sqlite3
from typing import Optional

class SQLiteDatabase:
    def __init__(self, db_path: str = "farmacia_vannesa.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            ''')
            
            # Products table (Advanced schema)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    generic_name TEXT NOT NULL,
                    product_code TEXT NOT NULL,
                    description TEXT,
                    stock INTEGER NOT NULL,
                    presentation TEXT NOT NULL,
                    laboratory TEXT NOT NULL,
                    expiration_date TEXT NOT NULL,
                    dose TEXT NOT NULL,
                    cost_price REAL NOT NULL,
                    sale_price REAL NOT NULL
                )
            ''')
            
            # Sales table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total REAL NOT NULL,
                    date TEXT NOT NULL
                )
            ''')
            
            # Sale Items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (sale_id) REFERENCES sales (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')

            # Clients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    identity_card TEXT UNIQUE NOT NULL,
                    email TEXT,
                    phone TEXT
                )
            ''')

            # Audit logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    details TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Run migrations for existing databases
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'cajero'")
            except sqlite3.OperationalError:
                # Column already exists
                pass

            try:
                cursor.execute("ALTER TABLE sales ADD COLUMN client_id INTEGER DEFAULT NULL REFERENCES clients(id)")
            except sqlite3.OperationalError:
                # Column already exists
                pass
            
            conn.commit()
