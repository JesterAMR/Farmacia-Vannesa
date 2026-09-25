import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import create_app
from app.infrastructure.database.sqlite_connection import SQLiteDatabase
from app.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository
from app.infrastructure.repositories.sqlite_product_repository import SQLiteProductRepository
from app.infrastructure.repositories.sqlite_sale_repository import SQLiteSaleRepository
from app.infrastructure.repositories.sqlite_client_repository import SQLiteClientRepository
from app.infrastructure.repositories.sqlite_audit_repository import SQLiteAuditRepository
from app.infrastructure.repositories.sqlite_cash_repository import SQLiteCashRepository
from app.infrastructure.repositories.sqlite_inventory_movement_repository import SQLiteInventoryMovementRepository

from app.application.services.auth_service import AuthService
from app.application.services.inventory_service import InventoryService
from app.application.services.sales_service import SalesService
from app.application.services.client_service import ClientService
from app.application.services.audit_service import AuditService
from app.application.services.cash_service import CashService
from app.application.services.inventory_movement_service import InventoryMovementService

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    db = SQLiteDatabase(db_path=path)
    yield db
    try:
        os.remove(path)
    except Exception:
        pass

@pytest.fixture
def repos(temp_db):
    return {
        "user": SQLiteUserRepository(temp_db),
        "product": SQLiteProductRepository(temp_db),
        "sale": SQLiteSaleRepository(temp_db),
        "client": SQLiteClientRepository(temp_db),
        "audit": SQLiteAuditRepository(temp_db),
        "cash": SQLiteCashRepository(temp_db),
        "movement": SQLiteInventoryMovementRepository(temp_db),
    }

@pytest.fixture
def services(repos):
    auth = AuthService(repos["user"])
    audit = AuditService(repos["audit"])
    inventory = InventoryService(repos["product"])
    client = ClientService(repos["client"])
    cash = CashService(repos["cash"])
    movement = InventoryMovementService(repos["movement"], repos["product"])
    sales = SalesService(
        sale_repository=repos["sale"],
        product_repository=repos["product"],
        inventory_movement_service=movement,
        cash_service=cash
    )
    return {
        "auth": auth,
        "audit": audit,
        "inventory": inventory,
        "client": client,
        "cash": cash,
        "movement": movement,
        "sales": sales
    }

@pytest.fixture
def app(temp_db):
    test_config = {
        "TESTING": True,
        "WTF_CSRF_ENABLED": False, # Permite pruebas de API HTTP directas
        "SECRET_KEY": "test_secret_key_12345"
    }
    app = create_app(test_config=test_config)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()
