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
            
            # Products table (Advanced schema con Regulación MINSA y DGI)
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
                    sale_price REAL NOT NULL,
                    sanitary_register TEXT DEFAULT 'MINSA-REG-2024-001',
                    batch_number TEXT DEFAULT 'LOT-GEN-01',
                    is_controlled INTEGER DEFAULT 0,
                    is_exempt_iva INTEGER DEFAULT 1,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Sales table (Con desglose fiscal DGI Ley 822 y receta MINSA Ley 292)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total REAL NOT NULL,
                    date TEXT NOT NULL,
                    client_id INTEGER REFERENCES clients(id),
                    subtotal_exempt REAL DEFAULT 0.0,
                    subtotal_taxable REAL DEFAULT 0.0,
                    iva_total REAL DEFAULT 0.0,
                    currency TEXT DEFAULT 'NIO',
                    exchange_rate REAL DEFAULT 36.62,
                    total_usd REAL DEFAULT 0.0,
                    prescription_doctor TEXT,
                    doctor_minsa_code TEXT,
                    prescription_number TEXT,
                    fiscal_xml TEXT,
                    dgi_auth_number TEXT
                )
            ''')
            
            # Sale Items table (Con trazabilidad de lote e IVA 15% / Exento)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    is_exempt INTEGER DEFAULT 1,
                    iva_rate REAL DEFAULT 0.0,
                    iva_amount REAL DEFAULT 0.0,
                    batch_number TEXT,
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

            # Cash shifts table (Apertura y Cierre de Caja)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cash_shifts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    shift_name TEXT NOT NULL DEFAULT 'Matutino',
                    register_name TEXT NOT NULL DEFAULT 'Caja #1 - Principal',
                    initial_amount REAL NOT NULL DEFAULT 0.0,
                    expected_cash REAL DEFAULT NULL,
                    physical_cash REAL DEFAULT NULL,
                    difference REAL DEFAULT NULL,
                    vault_deposit REAL DEFAULT NULL,
                    remnant_cash REAL DEFAULT NULL,
                    status TEXT NOT NULL DEFAULT 'Abierta',
                    notes TEXT,
                    opened_at TEXT NOT NULL,
                    closed_at TEXT DEFAULT NULL
                )
            ''')

            # Cash movements table (Egresos, Ingresos extraordinarios, Retiros)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cash_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shift_id INTEGER REFERENCES cash_shifts(id) ON DELETE SET NULL,
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    movement_type TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'Operativo',
                    concept TEXT NOT NULL,
                    amount REAL NOT NULL,
                    voucher_reference TEXT DEFAULT NULL,
                    created_at TEXT NOT NULL
                )
            ''')

            # Inventory movements table (Kardex de entradas, salidas y mermas)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    movement_type TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    previous_stock INTEGER NOT NULL DEFAULT 0,
                    new_stock INTEGER NOT NULL DEFAULT 0,
                    reason TEXT NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL
                )
            ''')


            # Run migrations for existing databases
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'cajero'")
            except sqlite3.OperationalError:
                pass

            try:
                cursor.execute("ALTER TABLE sales ADD COLUMN client_id INTEGER DEFAULT NULL REFERENCES clients(id)")
            except sqlite3.OperationalError:
                pass

            try:
                cursor.execute("ALTER TABLE products ADD COLUMN is_active INTEGER DEFAULT 1")
            except sqlite3.OperationalError:
                pass

            # Migraciones de Regulación Sanitaria MINSA y Fiscal DGI
            product_new_cols = [
                ("sanitary_register", "TEXT DEFAULT 'MINSA-REG-2024-001'"),
                ("batch_number", "TEXT DEFAULT 'LOT-GEN-01'"),
                ("is_controlled", "INTEGER DEFAULT 0"),
                ("is_exempt_iva", "INTEGER DEFAULT 1")
            ]
            for col_name, col_def in product_new_cols:
                try:
                    cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_def}")
                except sqlite3.OperationalError:
                    pass

            sales_new_cols = [
                ("subtotal_exempt", "REAL DEFAULT 0.0"),
                ("subtotal_taxable", "REAL DEFAULT 0.0"),
                ("iva_total", "REAL DEFAULT 0.0"),
                ("currency", "TEXT DEFAULT 'NIO'"),
                ("exchange_rate", "REAL DEFAULT 36.62"),
                ("total_usd", "REAL DEFAULT 0.0"),
                ("prescription_doctor", "TEXT DEFAULT NULL"),
                ("doctor_minsa_code", "TEXT DEFAULT NULL"),
                ("prescription_number", "TEXT DEFAULT NULL"),
                ("fiscal_xml", "TEXT DEFAULT NULL"),
                ("dgi_auth_number", "TEXT DEFAULT NULL")
            ]
            for col_name, col_def in sales_new_cols:
                try:
                    cursor.execute(f"ALTER TABLE sales ADD COLUMN {col_name} {col_def}")
                except sqlite3.OperationalError:
                    pass

            sale_items_new_cols = [
                ("is_exempt", "INTEGER DEFAULT 1"),
                ("iva_rate", "REAL DEFAULT 0.0"),
                ("iva_amount", "REAL DEFAULT 0.0"),
                ("batch_number", "TEXT DEFAULT NULL")
            ]
            for col_name, col_def in sale_items_new_cols:
                try:
                    cursor.execute(f"ALTER TABLE sale_items ADD COLUMN {col_name} {col_def}")
                except sqlite3.OperationalError:
                    pass

            # Enforce unique product code constraint at database level
            try:
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_products_code ON products(product_code)")
            except sqlite3.OperationalError:
                pass

            # Enforce positive sale quantity check at database level
            try:
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS check_sale_items_qty_positive 
                    BEFORE INSERT ON sale_items 
                    FOR EACH ROW 
                    BEGIN 
                        SELECT CASE WHEN NEW.quantity <= 0 THEN RAISE(ABORT, 'La cantidad vendida debe ser mayor a 0.') END; 
                    END;
                """)
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS check_sale_items_qty_positive_update 
                    BEFORE UPDATE ON sale_items 
                    FOR EACH ROW 
                    BEGIN 
                        SELECT CASE WHEN NEW.quantity <= 0 THEN RAISE(ABORT, 'La cantidad vendida debe ser mayor a 0.') END; 
                    END;
                """)
            except sqlite3.OperationalError:
                pass

            # Enforce non-negative stock and positive prices at database level (Validaciones estrictas)
            try:
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS check_product_constraints_insert
                    BEFORE INSERT ON products
                    FOR EACH ROW
                    BEGIN
                        SELECT CASE WHEN NEW.stock < 0 THEN RAISE(ABORT, 'El stock del producto no puede ser negativo.') END;
                        SELECT CASE WHEN NEW.sale_price <= 0 THEN RAISE(ABORT, 'El precio de venta debe ser estrictamente mayor a 0.') END;
                        SELECT CASE WHEN NEW.cost_price <= 0 THEN RAISE(ABORT, 'El costo del producto debe ser estrictamente mayor a 0.') END;
                    END;
                """)
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS check_product_constraints_update
                    BEFORE UPDATE ON products
                    FOR EACH ROW
                    BEGIN
                        SELECT CASE WHEN NEW.stock < 0 THEN RAISE(ABORT, 'El stock del producto no puede ser negativo.') END;
                        SELECT CASE WHEN NEW.sale_price <= 0 THEN RAISE(ABORT, 'El precio de venta debe ser estrictamente mayor a 0.') END;
                        SELECT CASE WHEN NEW.cost_price <= 0 THEN RAISE(ABORT, 'El costo del producto debe ser estrictamente mayor a 0.') END;
                    END;
                """)
            except sqlite3.OperationalError:
                pass

            # Enforce valid client identity card at database level
            try:
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS check_client_identity_card
                    BEFORE INSERT ON clients
                    FOR EACH ROW
                    BEGIN
                        SELECT CASE WHEN LENGTH(TRIM(NEW.identity_card)) < 3 THEN RAISE(ABORT, 'La Cédula o RUC del cliente debe ser válida.') END;
                    END;
                """)
            except sqlite3.OperationalError:
                pass
            
            conn.commit()
