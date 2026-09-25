import pytest

def test_inventory_create_and_get(services):
    inv = services["inventory"]
    p = inv.create_product(
        name="Paracetamol 500mg",
        generic_name="Acetaminofén",
        product_code="MED-PAR-01",
        description="Analgésico",
        stock=50,
        presentation="Caja 20 Tabletas",
        laboratory="Ramos",
        expiration_date="2027-12-31",
        dose="500mg",
        cost_price=10.0,
        sale_price=15.0
    )
    assert p.id is not None
    assert p.product_code == "MED-PAR-01"

    fetched = inv.get_product(p.id)
    assert fetched is not None
    assert fetched.name == "Paracetamol 500mg"
    assert fetched.stock == 50

def test_inventory_duplicate_product_code_raises_error(services):
    inv = services["inventory"]
    inv.create_product(
        name="Ibuprofeno 400mg",
        generic_name="Ibuprofeno",
        product_code="MED-IBU-01",
        description="Antiinflamatorio",
        stock=30,
        presentation="Caja 10 Cápsulas",
        laboratory="MK",
        expiration_date="2027-06-30",
        dose="400mg",
        cost_price=12.0,
        sale_price=20.0
    )

    with pytest.raises(ValueError, match="ya existe"):
        inv.create_product(
            name="Ibuprofeno Genérico",
            generic_name="Ibuprofeno",
            product_code="MED-IBU-01", # Mismo código
            description="Otro lab",
            stock=10,
            presentation="Caja",
            laboratory="Calox",
            expiration_date="2027-01-01",
            dose="400mg",
            cost_price=10.0,
            sale_price=18.0
        )

def test_inventory_restock(services):
    inv = services["inventory"]
    p = inv.create_product(
        name="Amoxicilina 500mg",
        generic_name="Amoxicilina",
        product_code="MED-AMX-01",
        description="Antibiótico",
        stock=20,
        presentation="Frasco",
        laboratory="Calox",
        expiration_date="2026-11-30",
        dose="500mg",
        cost_price=25.0,
        sale_price=35.0
    )
    updated = inv.restock_product(p.id, 15)
    assert updated.stock == 35
