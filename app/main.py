from flask import Flask, redirect, url_for
from flask_wtf.csrf import CSRFProtect
import os
import sys
import secrets
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("FarmaciaVannesa")

# Repositorios SQLite (Persistencia Local / Resiliencia BCP)
from app.infrastructure.database.sqlite_connection import SQLiteDatabase
from app.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository
from app.infrastructure.repositories.sqlite_product_repository import SQLiteProductRepository
from app.infrastructure.repositories.sqlite_sale_repository import SQLiteSaleRepository
from app.infrastructure.repositories.sqlite_client_repository import SQLiteClientRepository
from app.infrastructure.repositories.sqlite_audit_repository import SQLiteAuditRepository
from app.infrastructure.repositories.sqlite_cash_repository import SQLiteCashRepository
from app.infrastructure.repositories.sqlite_inventory_movement_repository import SQLiteInventoryMovementRepository

# Repositorios Supabase (Nube)
from app.infrastructure.repositories.supabase_user_repository import SupabaseUserRepository
from app.infrastructure.repositories.supabase_product_repository import SupabaseProductRepository
from app.infrastructure.repositories.supabase_sale_repository import SupabaseSaleRepository
from app.infrastructure.repositories.supabase_client_repository import SupabaseClientRepository
from app.infrastructure.repositories.supabase_audit_repository import SupabaseAuditRepository
from app.infrastructure.repositories.supabase_cash_repository import SupabaseCashRepository
from app.infrastructure.repositories.supabase_inventory_movement_repository import SupabaseInventoryMovementRepository

# Servicios
from app.application.services.auth_service import AuthService
from app.application.services.inventory_service import InventoryService
from app.application.services.sales_service import SalesService
from app.application.services.dashboard_service import DashboardService
from app.application.services.client_service import ClientService
from app.application.services.audit_service import AuditService
from app.application.services.cash_service import CashService
from app.application.services.inventory_movement_service import InventoryMovementService

# Blueprints
from app.presentation.routes.auth import create_auth_blueprint
from app.presentation.routes.dashboard_routes import create_dashboard_blueprint
from app.presentation.routes.inventory_routes import create_inventory_blueprint
from app.presentation.routes.sales_routes import create_sales_blueprint
from app.presentation.routes.client_routes import create_client_blueprint
from app.presentation.routes.cash_routes import create_cash_blueprint
from app.presentation.routes.inventory_movement_routes import create_inventory_movement_blueprint
from app.presentation.routes.stats_routes import create_stats_blueprint

csrf = CSRFProtect()

def _check_supabase_available() -> bool:
    """Valida si Supabase está configurado y si las tablas de la aplicación ya existen."""
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()
    if not url or not key:
        return False
    try:
        from app.infrastructure.database.supabase_connection import get_supabase_client
        sb = get_supabase_client()
        # Verificar si la tabla 'users' existe y responde
        sb.table('users').select('id').limit(1).execute()
        return True
    except Exception as e:
        logger.warning(f"Supabase Cloud no disponible o tablas no inicializadas: {e}")
        return False

def create_app(test_config=None):
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(os.path.dirname(__file__))

    project_root = os.path.dirname(base_dir) if os.path.basename(base_dir) == 'app' else base_dir

    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'presentation', 'templates'),
                static_folder=os.path.join(base_dir, 'presentation', 'static'))

    # Configuración de Seguridad: SECRET_KEY
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        secret_file = os.path.join(project_root, '.secret_key')
        if os.path.exists(secret_file):
            try:
                with open(secret_file, 'r', encoding='utf-8') as f:
                    secret_key = f.read().strip()
            except Exception:
                secret_key = None
        if not secret_key:
            secret_key = secrets.token_hex(32)
            try:
                with open(secret_file, 'w', encoding='utf-8') as f:
                    f.write(secret_key)
            except Exception:
                pass

    app.config['SECRET_KEY'] = secret_key

    # Soporte para sobreescritura en tests
    if test_config:
        app.config.update(test_config)

    # Inicializar CSRF Protection
    csrf.init_app(app)

    # Determinar modo de persistencia (Dual-Mode Architecture)
    db_path = os.path.join(project_root, 'vannesa_db.sqlite')
    sqlite_db = SQLiteDatabase(db_path=db_path)

    force_sqlite = os.environ.get('USE_SQLITE', '0').lower() in ('1', 'true')
    use_supabase = (not force_sqlite) and _check_supabase_available()

    if use_supabase:
        logger.info("[Arquitectura TI] Modo de Persistencia Activo: SUPABASE CLOUD (PostgreSQL)")
        user_repo = SupabaseUserRepository()
        product_repo = SupabaseProductRepository()
        sale_repo = SupabaseSaleRepository()
        client_repo = SupabaseClientRepository()
        audit_repo = SupabaseAuditRepository()
        cash_repo = SupabaseCashRepository()
        movement_repo = SupabaseInventoryMovementRepository()
    else:
        logger.info("[Arquitectura TI] Modo de Persistencia Activo: SQLITE LOCAL RESILIENTE (Modo Contingencia / BCP)")
        user_repo = SQLiteUserRepository(sqlite_db)
        product_repo = SQLiteProductRepository(sqlite_db)
        sale_repo = SQLiteSaleRepository(sqlite_db)
        client_repo = SQLiteClientRepository(sqlite_db)
        audit_repo = SQLiteAuditRepository(sqlite_db)
        cash_repo = SQLiteCashRepository(sqlite_db)
        movement_repo = SQLiteInventoryMovementRepository(sqlite_db)

    # Inicialización de Servicios de Lógica de Negocio
    auth_service = AuthService(user_repository=user_repo)
    audit_service = AuditService(audit_repository=audit_repo)
    inventory_service = InventoryService(product_repository=product_repo)
    client_service = ClientService(client_repository=client_repo)
    cash_service = CashService(cash_repository=cash_repo)
    inventory_movement_service = InventoryMovementService(
        movement_repository=movement_repo,
        product_repository=product_repo
    )
    sales_service = SalesService(
        sale_repository=sale_repo,
        product_repository=product_repo,
        inventory_movement_service=inventory_movement_service,
        cash_service=cash_service
    )
    dashboard_service = DashboardService(
        sale_repository=sale_repo,
        product_repository=product_repo,
        audit_service=audit_service
    )

    # Registro de Blueprints con Inyección de Dependencias
    auth_bp = create_auth_blueprint(auth_service, audit_service)
    dashboard_bp = create_dashboard_blueprint(dashboard_service)
    inventory_bp = create_inventory_blueprint(inventory_service, audit_service)
    sales_bp = create_sales_blueprint(sales_service, inventory_service, client_service, audit_service, product_repo)
    client_bp = create_client_blueprint(client_service, audit_service)
    cash_bp = create_cash_blueprint(cash_service, audit_service)
    inventory_movement_bp = create_inventory_movement_blueprint(inventory_movement_service, inventory_service, audit_service)
    stats_bp = create_stats_blueprint(inventory_service, sales_service)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(cash_bp)
    app.register_blueprint(inventory_movement_bp)
    app.register_blueprint(stats_bp)

    return app

# Instancia WSGI para producción (Gunicorn en Render o Procfile)
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0').lower() in ('1', 'true')
    print(f"Iniciando servidor Farmacia Vannesa en http://0.0.0.0:{port} (Debug: {debug})")
    app.run(debug=debug, host='0.0.0.0', port=port)