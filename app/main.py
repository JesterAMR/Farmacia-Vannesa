from flask import Flask, redirect, url_for
import os
import sys

# 1. ELIMINAMOS las importaciones de SQLite (las dejamos comentadas o las borras)
# from app.infrastructure.database.sqlite_connection import SQLiteDatabase
# from app.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository
# from app.infrastructure.repositories.sqlite_product_repository import SQLiteProductRepository
# from app.infrastructure.repositories.sqlite_sale_repository import SQLiteSaleRepository
# from app.infrastructure.repositories.sqlite_client_repository import SQLiteClientRepository

# 2. AGREGAMOS las importaciones de Supabase
from app.infrastructure.repositories.supabase_user_repository import SupabaseUserRepository
from app.infrastructure.repositories.supabase_product_repository import SupabaseProductRepository
from app.infrastructure.repositories.supabase_sale_repository import SupabaseSaleRepository
from app.infrastructure.repositories.supabase_client_repository import SupabaseClientRepository
from app.infrastructure.repositories.supabase_audit_repository import SupabaseAuditRepository

from app.application.services.auth_service import AuthService
from app.application.services.inventory_service import InventoryService
from app.application.services.sales_service import SalesService
from app.application.services.dashboard_service import DashboardService
from app.application.services.client_service import ClientService
from app.application.services.audit_service import AuditService
from app.presentation.routes.auth import create_auth_blueprint
from app.presentation.routes.dashboard_routes import create_dashboard_blueprint
from app.presentation.routes.inventory_routes import create_inventory_blueprint
from app.presentation.routes.sales_routes import create_sales_blueprint
from app.presentation.routes.client_routes import create_client_blueprint


def create_app():
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running in a normal Python environment
        base_dir = os.path.abspath(os.path.dirname(__file__))
    
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'presentation', 'templates'),
                static_folder=os.path.join(base_dir, 'presentation', 'static'))
    
    app.config['SECRET_KEY'] = 'vannesa_secret_key_123_456_super_seguro'
    
    # 3. ELIMINAMOS la inicialización de SQLite
    # db_path = os.path.join(base_dir, 'vannesa_db.sqlite')
    # database = SQLiteDatabase(db_path=db_path)
    
    # 4. INSTANCIAMOS los Repositorios de Supabase
    # Nota: Según los archivos que creamos, estos no necesitan recibir 'database' 
    # en el __init__ porque ya llaman a get_supabase_client() por dentro.
    user_repo = SupabaseUserRepository()
    product_repo = SupabaseProductRepository()
    sale_repo = SupabaseSaleRepository()
    client_repo = SupabaseClientRepository()
    audit_repo = SupabaseAuditRepository() # Nuevo repo para auditoría
    
    # 5. Servicios Lógica de Negocio (¡Intactos!)
    # Excepto AuditService, que asumo que antes recibía 'db=database'. 
    # Ahora probablemente deberías pasarle el audit_repo.
    auth_service = AuthService(user_repository=user_repo)
    inventory_service = InventoryService(product_repository=product_repo)
    client_service = ClientService(client_repository=client_repo)
    audit_service = AuditService(audit_repository=audit_repo) # <-- AJUSTE AQUÍ
    sales_service = SalesService(sale_repository=sale_repo, product_repository=product_repo)
    dashboard_service = DashboardService(sale_repository=sale_repo, product_repository=product_repo, audit_service=audit_service)

    # Blueprints (¡Intactos!)
    auth_bp = create_auth_blueprint(auth_service)
    dashboard_bp = create_dashboard_blueprint(dashboard_service)
    inventory_bp = create_inventory_blueprint(inventory_service, audit_service)
    sales_bp = create_sales_blueprint(sales_service, inventory_service, client_service, audit_service, product_repo)
    client_bp = create_client_blueprint(client_service, audit_service)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(client_bp)

    # Blueprints adicionales (Caja, Movimientos de Inventario y Estadísticas)
    try:
        from app.presentation.routes.cash_routes import create_cash_blueprint
        app.register_blueprint(create_cash_blueprint())
    except Exception as e:
        import logging
        logging.warning(f"No se pudo registrar cash_blueprint: {e}")

    try:
        from app.presentation.routes.inventory_movement_routes import create_inventory_movement_blueprint
        app.register_blueprint(create_inventory_movement_blueprint())
    except Exception as e:
        import logging
        logging.warning(f"No se pudo registrar inventory_movement_blueprint: {e}")

    try:
        from app.presentation.routes.stats_routes import create_stats_blueprint
        app.register_blueprint(create_stats_blueprint())
    except Exception as e:
        import logging
        logging.warning(f"No se pudo registrar stats_blueprint: {e}")

    return app

# Instancia para servidores de producción WSGI (Gunicorn en Render: gunicorn app.main:app)
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Iniciando servidor de Farmacia Vannesa v2 en http://0.0.0.0:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)