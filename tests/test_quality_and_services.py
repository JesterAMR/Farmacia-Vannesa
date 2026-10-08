# -*- coding: utf-8 -*-
"""
Suite de Pruebas de Calidad, Límites y Servicios de Negocio para Farmacia Vannesa.
Aumenta la cobertura de pruebas por encima del umbral del 80% (Auditoría A-12 / PRU-TST-01),
comprueba valores límite (PRU-TST-03) y valida el endpoint de monitoreo /health (Auditoría A-20 / PRU-DES-05).
"""

import pytest
import datetime
from app.domain.models.product import Product
from app.application.services.dashboard_service import DashboardService

def test_client_service_crud_and_validations(services):
    client_srv = services["client"]
    
    # 1. Creación exitosa
    c1 = client_srv.create_client(
        name="María González",
        identity_card="001-010190-0001A",
        email="maria@farmacia.com",
        phone="8888-1234"
    )
    assert c1.id is not None
    assert c1.name == "María González"
    assert c1.identity_card == "001-010190-0001A"

    # 2. Validación: No permitir identificación duplicada
    with pytest.raises(ValueError, match="Ya existe un cliente"):
        client_srv.create_client(name="Otro", identity_card="001-010190-0001A")

    # 3. Validación: Campos requeridos obligatorios
    with pytest.raises(ValueError, match="requeridos"):
        client_srv.create_client(name="", identity_card="123")

    # 4. Búsqueda y listado
    fetched = client_srv.get_client_by_identity("001-010190-0001A")
    assert fetched is not None
    assert fetched.id == c1.id

    all_clients = client_srv.get_all_clients()
    assert len(all_clients) >= 1

    # 5. Actualización exitosa
    updated = client_srv.update_client(
        id=c1.id,
        name="María González de López",
        identity_card="001-010190-0001A",
        email="maria.lopez@farmacia.com",
        phone="8888-5678"
    )
    assert updated.name == "María González de López"
    assert updated.phone == "8888-5678"

    # 6. Validación de actualización con id inexistente
    with pytest.raises(ValueError, match="no encontrado"):
        client_srv.update_client(id=99999, name="Inexistente", identity_card="999-999999-9999X")

    # 7. Eliminación
    del_ok = client_srv.delete_client(c1.id)
    assert del_ok is True
    assert client_srv.get_client(c1.id) is None

def test_dashboard_service_metrics_and_alerts(services, repos):
    prod_repo = repos["product"]
    sale_repo = repos["sale"]
    audit_srv = services["audit"]
    
    dashboard_srv = DashboardService(
        sale_repository=sale_repo,
        product_repository=prod_repo,
        audit_service=audit_srv
    )

    # Insertar productos con diferentes fechas y stock para probar métricas
    today = datetime.date.today()
    expired_date = (today - datetime.timedelta(days=10)).strftime("%Y-%m-%d")
    soon_expiring_date = (today + datetime.timedelta(days=30)).strftime("%Y-%m-%d")

    p1 = Product(
        name="Paracetamol 500mg",
        generic_name="Paracetamol",
        product_code="MED-001",
        description="Analgésico",
        stock=5, # Bajo stock (<10)
        presentation="Caja 20 tabletas",
        laboratory="Bayer",
        expiration_date=expired_date, # Vencido
        dose="500mg",
        cost_price=10.0,
        sale_price=15.0
    )
    prod_repo.add(p1)

    p2 = Product(
        name="Amoxicilina 250mg",
        generic_name="Amoxicilina",
        product_code="MED-002",
        description="Antibiótico",
        stock=25, # Stock normal
        presentation="Frasco 100ml",
        laboratory="MK",
        expiration_date=soon_expiring_date, # Próximo a vencer
        dose="250mg/5ml",
        cost_price=50.0,
        sale_price=75.0
    )
    prod_repo.add(p2)

    # 1. Probar rangos por defecto y semanales
    summary_7d = dashboard_srv.get_summary()
    assert "total_revenue" in summary_7d
    assert summary_7d["low_stock_count"] >= 1
    assert summary_7d["total_items"] >= 30

    # 2. Verificar detección de productos vencidos y próximos a vencer
    exp_products = summary_7d["expiring_products"]
    statuses = [ep["status"] for ep in exp_products]
    assert "Vencido" in statuses or "Próximo a vencer" in statuses

    # 3. Probar otros rangos de tiempo (weekly, biweekly, monthly, custom)
    assert dashboard_srv.get_summary_for_range("weekly") is not None
    assert dashboard_srv.get_summary_for_range("biweekly") is not None
    assert dashboard_srv.get_summary_for_range("monthly") is not None
    assert dashboard_srv.get_summary_for_range(
        "custom",
        start_date_str=(today - datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
        end_date_str=today.strftime("%Y-%m-%d")
    ) is not None

def test_inventory_boundary_and_valuation(services):
    inv_srv = services["inventory"]

    # Crear producto con 11 atributos completos
    p = inv_srv.create_product(
        name="Ibuprofeno 400mg",
        generic_name="Ibuprofeno",
        product_code="MED-IBU-400",
        description="Antiinflamatorio",
        stock=12,
        presentation="Caja 10 cápsulas",
        laboratory="Genfar",
        expiration_date="2027-12-31",
        dose="400mg",
        cost_price=15.0,
        sale_price=22.0
    )
    assert p.id is not None
    assert p.stock == 12

    # Intentar registrar otro producto con el mismo código (Validación de unicidad)
    with pytest.raises(ValueError, match="ya existe"):
        inv_srv.create_product(
            name="Ibuprofeno Genérico",
            generic_name="Ibuprofeno",
            product_code="MED-IBU-400", # Duplicado
            description="Antiinflamatorio",
            stock=5,
            presentation="Caja 10 cápsulas",
            laboratory="Genfar",
            expiration_date="2027-12-31",
            dose="400mg",
            cost_price=10.0,
            sale_price=15.0
        )

    # Restock de producto
    restocked = inv_srv.restock_product(p.id, 8)
    assert restocked is not None
    assert restocked.stock == 20

    # Valoración de inventario
    valuation = inv_srv.get_inventory_valuation()
    assert valuation["total_items"] >= 20
    assert valuation["total_cost_value"] > 0
    assert valuation["total_sale_value"] > 0

def test_sales_boundary_stock_rules(services):
    inv_srv = services["inventory"]
    sales_srv = services["sales"]

    # Crear producto con exactamente 2 unidades
    p = inv_srv.create_product(
        name="Loratadina 10mg",
        generic_name="Loratadina",
        product_code="MED-LOR-10",
        description="Antihistamínico",
        stock=2,
        presentation="Caja 10 tabletas",
        laboratory="Ramos",
        expiration_date="2027-01-01",
        dose="10mg",
        cost_price=8.0,
        sale_price=12.0
    )

    # 1. Caso Límite Excedido: Intentar vender 3 unidades (debe fallar con ValueError)
    items_over = [{"product_id": p.id, "quantity": 3}]
    with pytest.raises(ValueError, match="insuficiente"):
        sales_srv.create_sale(items_data=items_over)

    # 2. Caso Cantidad Cero o Negativa: debe fallar
    items_neg = [{"product_id": p.id, "quantity": -1}]
    with pytest.raises(ValueError, match="mayor a cero"):
        sales_srv.create_sale(items_data=items_neg)

    # 3. Caso Límite Exacto: Vender exactamente las 2 unidades disponibles
    items_exact = [{"product_id": p.id, "quantity": 2}]
    sale = sales_srv.create_sale(items_data=items_exact)
    assert sale.id is not None
    assert sale.total == 24.0

    # 4. Verificar que el stock resultante quede en cero (0)
    updated_p = inv_srv.get_product(p.id)
    assert updated_p.stock == 0

    # 5. Caso Límite Stock Cero: Intentar vender 1 unidad más cuando stock es 0
    items_zero = [{"product_id": p.id, "quantity": 1}]
    with pytest.raises(ValueError, match="insuficiente"):
        sales_srv.create_sale(items_data=items_zero)

def test_health_check_endpoint(client):
    """Verifica que el endpoint /health responda 200 OK con JSON estructurado."""
    res = client.get('/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data is not None
    assert data["status"] == "UP"
    assert "database_mode" in data
    assert "version" in data
    assert data["service"] == "Farmacia Vannesa API"

def test_inventory_movement_operations(services):
    inv_srv = services["inventory"]
    mov_srv = services["movement"]

    prod = inv_srv.create_product(
        name="Amoxicilina 500mg",
        generic_name="Amoxicilina",
        product_code="MED-AMOX-500",
        description="Antibiótico",
        stock=10,
        presentation="Caja 30 cápsulas",
        laboratory="MK",
        expiration_date="2027-06-30",
        dose="500mg",
        cost_price=30.0,
        sale_price=45.0
    )

    # 1. Entrada de inventario
    m_in = mov_srv.register_movement(
        product_id=prod.id,
        movement_type="Entrada por Compra",
        quantity=15,
        reason="Factura Proveedor #1002"
    )
    assert m_in.id is not None
    assert m_in.quantity == 15
    assert inv_srv.get_product(prod.id).stock == 25

    # 2. Salida por Merma / Vencimiento
    m_out = mov_srv.register_movement(
        product_id=prod.id,
        movement_type="Merma / Daño",
        quantity=5,
        reason="Empaque roto en traslado"
    )
    assert m_out.id is not None
    assert m_out.quantity == -5
    assert inv_srv.get_product(prod.id).stock == 20

    # 3. Validación: Salida mayor al stock disponible
    with pytest.raises(ValueError, match="insuficiente"):
        mov_srv.register_movement(
            product_id=prod.id,
            movement_type="Salida",
            quantity=999,
            reason="Exceso"
        )

    # 4. Validación: Cantidad negativa o cero
    with pytest.raises(ValueError, match="mayor a cero"):
        mov_srv.register_movement(
            product_id=prod.id,
            movement_type="Entrada",
            quantity=0,
            reason="Invalido"
        )

    # 5. Listado y métricas
    history = mov_srv.get_product_movements(prod.id)
    assert len(history) >= 2
    metrics = mov_srv.get_metrics()
    assert isinstance(metrics, dict)

def test_nicaragua_regulatory_minsa_and_dgi_fiscal(services):
    """Verifica cumplimiento de Ley 292 (MINSA) y Ley 822 (DGI Facturación Fiscal)."""
    inv_srv = services["inventory"]
    sales_srv = services["sales"]

    # 1. Crear producto con Registro Sanitario MINSA y Lote (Exento de IVA - Art. 153 LCT)
    p_exento = inv_srv.create_product(
        name="Paracetamol 500mg MK",
        generic_name="Paracetamol",
        product_code="MED-PCM-500",
        description="Analgésico",
        stock=20,
        presentation="Caja 20 tabletas",
        laboratory="MK",
        expiration_date="2027-10-31",
        dose="500mg",
        cost_price=10.0,
        sale_price=20.0,
        sanitary_register="MINSA-REG-2024-0012",
        batch_number="LOT-2026-A1",
        is_controlled=False,
        is_exempt_iva=True
    )
    assert p_exento.sanitary_register == "MINSA-REG-2024-0012"
    assert p_exento.batch_number == "LOT-2026-A1"

    # 2. Crear producto cosmético gravado con IVA 15%
    p_gravado = inv_srv.create_product(
        name="Bloqueador Solar SPF 50",
        generic_name="Protector Solar",
        product_code="COS-SUN-050",
        description="Cuidado de la piel",
        stock=10,
        presentation="Frasco 120ml",
        laboratory="Nivea",
        expiration_date="2028-05-15",
        dose="120ml",
        cost_price=100.0,
        sale_price=200.0,
        sanitary_register="MINSA-COS-2023-098",
        batch_number="LOT-2026-SUN",
        is_controlled=False,
        is_exempt_iva=False
    )
    assert p_gravado.is_exempt_iva is False

    # 3. Crear producto controlado (Psicotrópico)
    p_controlado = inv_srv.create_product(
        name="Clonazepam 2mg",
        generic_name="Clonazepam",
        product_code="MED-CLZ-002",
        description="Ansiolítico controlado",
        stock=10,
        presentation="Caja 30 tabletas",
        laboratory="Roche",
        expiration_date="2027-12-31",
        dose="2mg",
        cost_price=50.0,
        sale_price=80.0,
        sanitary_register="MINSA-PSI-2022-044",
        batch_number="LOT-CLZ-99",
        is_controlled=True,
        is_exempt_iva=True
    )

    # 4. Intentar vender medicamento controlado sin datos de médico: debe fallar por Ley 292
    with pytest.raises(ValueError, match="médico prescriptor"):
        sales_srv.create_sale(items_data=[{"product_id": p_controlado.id, "quantity": 1}])

    # 5. Venta mixta legal con receta y desglose fiscal DGI
    sale = sales_srv.create_sale(
        items_data=[
            {"product_id": p_exento.id, "quantity": 2},     # 2 * 20 = 40 (Exento)
            {"product_id": p_gravado.id, "quantity": 1},    # 1 * 200 = 200 + 30 IVA = 230
            {"product_id": p_controlado.id, "quantity": 1}   # 1 * 80 = 80 (Exento)
        ],
        prescription_doctor="Dr. Carlos Mendoza",
        doctor_minsa_code="MINSA-MED-9941",
        prescription_number="REC-2026-0811"
    )

    # Total esperado: 40 + 80 = 120 exento; 200 gravado; IVA = 30; Total = 350
    assert sale.subtotal_exempt == 120.0
    assert sale.subtotal_taxable == 200.0
    assert sale.iva_total == 30.0
    assert sale.total == 350.0
    assert sale.total_usd == round(350.0 / 36.62, 2)
    assert sale.dgi_auth_number is not None
    assert "FacturaElectronica" in sale.fiscal_xml
    assert "Dr. Carlos Mendoza" in sale.fiscal_xml

def test_pagination_inventory_and_clients(services):
    """Verifica que la paginación funcione correctamente en inventario y clientes."""
    inv_srv = services["inventory"]
    cli_srv = services["client"]

    # Probar paginación de inventario
    page_1 = inv_srv.get_paginated_products(page=1, per_page=2)
    assert "items" in page_1
    assert "total" in page_1
    assert len(page_1["items"]) <= 2
    assert page_1["page"] == 1
    assert page_1["total_pages"] >= 1

    # Probar paginación de clientes
    cli_srv.create_client(name="Cliente Paginacion A", identity_card="001-010190-0001A")
    cli_srv.create_client(name="Cliente Paginacion B", identity_card="001-010190-0002B")
    cli_srv.create_client(name="Cliente Paginacion C", identity_card="001-010190-0003C")

    cli_pag = cli_srv.get_paginated_clients(page=1, per_page=2)
    assert len(cli_pag["items"]) == 2
    assert cli_pag["total"] >= 3
    assert cli_pag["total_pages"] >= 2
    assert cli_pag["has_next"] is True


