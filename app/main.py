from flask import Flask, redirect, url_for, request, g, jsonify
from flask_wtf.csrf import CSRFProtect
import os
import sys
import secrets
import logging
from logging.handlers import RotatingFileHandler
import time
import platform
import socket
import shutil
import datetime
from dotenv import load_dotenv

SERVER_START_TIME = time.time()

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

    # ----------------------------------------------------
    # Monitoreo y Logging Estructurado (Auditoría A-20 / Nivel 2)
    # ----------------------------------------------------
    logs_dir = os.path.join(project_root, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, 'farmacia_vannesa.log')

    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
        ))
        logger.addHandler(file_handler)
        app.logger.addHandler(file_handler)

    @app.before_request
    def record_start_time():
        g.start_time = time.time()

    @app.after_request
    def log_response_info(response):
        if hasattr(g, 'start_time') and not request.path.startswith('/static'):
            elapsed_ms = (time.time() - g.start_time) * 1000
            logger.info(f"[HTTP] {request.method} {request.path} -> {response.status_code} ({elapsed_ms:.1f}ms) IP: {request.remote_addr}")
        return response

    # ----------------------------------------------------
    # Endpoint de Health Check (Auditoría A-25 / PRU-DES-05)
    # Monitoreo integral: Servidor, SO, Catálogo de APIs, Base de Datos y Telemetría
    # ----------------------------------------------------
    @app.route('/health', methods=['GET'])
    @csrf.exempt
    def health_check():
        t0 = time.time()
        db_status = "ok"
        mode = "supabase" if use_supabase else "sqlite"
        db_latency_ms = 0.0
        sqlite_details = {}
        supabase_details = {}

        # 1. Chequeo de Base de Datos y Persistencia
        t_db_start = time.time()
        try:
            if use_supabase:
                if not _check_supabase_available():
                    db_status = "degraded"
                db_latency_ms = round((time.time() - t_db_start) * 1000, 2)
                sb_url = os.environ.get("SUPABASE_URL", "").strip()
                supabase_details = {
                    "configured": bool(sb_url),
                    "url": (sb_url[:24] + "...") if len(sb_url) > 24 else sb_url,
                    "status": "connected" if db_status == "ok" else "degraded",
                    "latency_ms": db_latency_ms
                }
            else:
                with sqlite_db.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT 1").fetchone()
                    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()
                    integrity = cur.execute("PRAGMA integrity_check;").fetchone()
                db_latency_ms = round((time.time() - t_db_start) * 1000, 2)
                db_size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0
                sqlite_details = {
                    "database_file": os.path.basename(db_path),
                    "integrity_status": integrity[0] if integrity else "unknown",
                    "size_kb": round(db_size_bytes / 1024, 2),
                    "tables_count": len(tables),
                    "tables": [t[0] for t in tables],
                    "latency_ms": db_latency_ms
                }
                sb_url = os.environ.get("SUPABASE_URL", "").strip()
                supabase_details = {
                    "configured": bool(sb_url),
                    "url": (sb_url[:24] + "...") if len(sb_url) > 24 else sb_url,
                    "status": "offline_contingency",
                    "note": "Modo BCP / SQLite local resiliente activo"
                }
        except Exception as err:
            db_status = f"unhealthy: {err}"
            logger.error(f"[HealthCheck] Error de verificación de base de datos: {err}")

        # 2. Información del Servidor y Sistema Operativo
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        uptime_seconds = round(time.time() - SERVER_START_TIME, 1)
        uptime_m, uptime_s = divmod(int(uptime_seconds), 60)
        uptime_h, uptime_m = divmod(uptime_m, 60)
        uptime_d, uptime_h = divmod(uptime_h, 24)
        uptime_human = f"{uptime_d}d {uptime_h}h {uptime_m}m {uptime_s}s" if uptime_d else (
            f"{uptime_h}h {uptime_m}m {uptime_s}s" if uptime_h else f"{uptime_m}m {uptime_s}s"
        )

        disk_info = {}
        try:
            total, used, free = shutil.disk_usage(project_root)
            disk_info = {
                "total_gb": round(total / (1024 ** 3), 2),
                "used_gb": round(used / (1024 ** 3), 2),
                "free_gb": round(free / (1024 ** 3), 2),
                "used_percentage": round((used / total) * 100, 1)
            }
        except Exception:
            disk_info = {"status": "unavailable"}

        server_info = {
            "hostname": socket.gethostname(),
            "operating_system": platform.platform(),
            "os_name": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "process_id": os.getpid(),
            "disk_storage": disk_info,
            "server_time_utc": now_utc.isoformat()
        }

        # 3. Mapeo y Catálogo de APIs / Módulos Registrados
        module_metadata = {
            "auth": {
                "name": "Autenticación y Seguridad (RBAC)",
                "description": "Control de acceso, login, logout y roles de usuario (Admin, Farmacéutico, Cajero)"
            },
            "inventory": {
                "name": "Catálogo e Inventario Farmacéutico",
                "description": "Gestión de medicamentos con 11 campos mandatorios, existencias y fechas de vencimiento"
            },
            "sales": {
                "name": "Punto de Venta (POS) y Facturación",
                "description": "Venta al mostrador, tickets y validación atómica anti-sobreventa (RF06)"
            },
            "client": {
                "name": "Gestión de Pacientes y Clientes",
                "description": "Directorio de clientes, historial de consumo y datos de contacto"
            },
            "cash": {
                "name": "Control de Caja Chica y Arqueos",
                "description": "Apertura de turno, movimientos de caja menor y balances de corte"
            },
            "inventory_movements": {
                "name": "Kardex y Movimientos de Inventario",
                "description": "Trazabilidad de entradas por compras, salidas por mermas y ajustes de inventario"
            },
            "dashboard": {
                "name": "Panel Analítico y Resumen Ejecutivo",
                "description": "Métricas consolidadas, alertas de stock mínimo y gráficos semanales/mensuales"
            },
            "stats": {
                "name": "Estadísticas y Proyecciones",
                "description": "Análisis estadístico de rotación y proyecciones de demanda farmacéutica"
            },
            "core": {
                "name": "Servicios Core / Monitoreo",
                "description": "Endpoints de telemetría, salud del sistema y archivos estáticos"
            }
        }

        modules_grouped = {}
        total_routes = 0
        for rule in app.url_map.iter_rules():
            total_routes += 1
            endpoint = rule.endpoint
            bp = endpoint.split('.')[0] if '.' in endpoint else 'core'
            if bp not in modules_grouped:
                meta = module_metadata.get(bp, {"name": bp.capitalize(), "description": f"Módulo {bp}"})
                modules_grouped[bp] = {
                    "module_id": bp,
                    "name": meta["name"],
                    "description": meta["description"],
                    "routes_count": 0,
                    "endpoints": []
                }
            methods = sorted(list(rule.methods - {'HEAD', 'OPTIONS'})) if rule.methods else []
            modules_grouped[bp]["routes_count"] += 1
            modules_grouped[bp]["endpoints"].append({
                "rule": str(rule),
                "endpoint": endpoint,
                "methods": methods
            })

        apis_info = {
            "total_endpoints": total_routes,
            "total_modules": len(modules_grouped),
            "modules": list(modules_grouped.values()),
            "external_integrations": {
                "supabase_cloud": supabase_details
            }
        }

        # 4. Telemetría y Seguridad
        is_healthy = "unhealthy" not in db_status.lower()
        overall_status = "UP" if is_healthy and db_status == "ok" else ("DEGRADED" if is_healthy else "DOWN")

        telemetry_info = {
            "csrf_protection": "active",
            "session_security": "Secure Secret Key (CSRF / HttpOnly)",
            "logging": {
                "level": "INFO",
                "file": "logs/farmacia_vannesa.log",
                "rotation": "5 MB (5 backups rotativos)",
                "structured_access_logs": "active"
            },
            "audit_standards": [
                "ISO/IEC 25010:2011 (Calidad de Software y Eficiencia)",
                "ISO 19011:2018 (Directrices de Auditoría Informática)",
                "ISO 22301:2019 (Resiliencia Operativa y Continuidad DRP)"
            ],
            "response_time_ms": round((time.time() - t0) * 1000, 2)
        }

        # 5. Estructura de Respuesta JSON (Preservando Compatibilidad)
        response_data = {
            "status": overall_status,
            "service": "Farmacia Vannesa API",
            "version": "1.0.0",
            "environment": "production" if not app.config.get("TESTING") else "testing",
            "timestamp": now_utc.isoformat(),
            "uptime_seconds": uptime_seconds,
            "uptime_human": uptime_human,
            "database_mode": mode,
            "database_status": db_status,
            "server": server_info,
            "database": {
                "active_mode": mode,
                "status": db_status,
                "latency_ms": db_latency_ms,
                "details": sqlite_details if not use_supabase else supabase_details
            },
            "apis": apis_info,
            "telemetry": telemetry_info
        }

        http_code = 200 if is_healthy else 503
        return jsonify(response_data), http_code

    return app

# Instancia WSGI para producción (Gunicorn en Render o Procfile)
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0').lower() in ('1', 'true')
    print(f"Iniciando servidor Farmacia Vannesa en http://0.0.0.0:{port} (Debug: {debug})")
    app.run(debug=debug, host='0.0.0.0', port=port)