import pytest

def test_sale_creation_and_stock_deduction(services):
    inv = services["inventory"]
    sales = services["sales"]

    p = inv.create_product(
        name="Loratadina 10mg",
        generic_name="Loratadina",
        product_code="MED-LOR-01",
        description="Antihistamínico",
        stock=25,
        presentation="Caja 10 Tabletas",
        laboratory="Ramos",
        expiration_date="2027-08-15",
        dose="10mg",
        cost_price=8.0,
        sale_price=12.0
    )

    sale = sales.create_sale(
        items_data=[{"product_id": p.id, "quantity": 5}]
    )
    assert sale.id is not None
    assert sale.total == 60.0 # 5 * 12.0

    updated_product = inv.get_product(p.id)
    assert updated_product.stock == 20 # 25 - 5

def test_sale_insufficient_stock_fails_and_preserves_stock(services):
    inv = services["inventory"]
    sales = services["sales"]

    p = inv.create_product(
        name="Omeprazol 20mg",
        generic_name="Omeprazol",
        product_code="MED-OME-01",
        description="Antiácido",
        stock=5,
        presentation="Caja 14 Cápsulas",
        laboratory="MK",
        expiration_date="2027-10-10",
        dose="20mg",
        cost_price=15.0,
        sale_price=25.0
    )

    with pytest.raises(ValueError, match="Stock insuficiente"):
        sales.create_sale(
            items_data=[{"product_id": p.id, "quantity": 10}]
        )

    # El stock original debe permanecer intacto
    product_after = inv.get_product(p.id)
    assert product_after.stock == 5

def test_sale_negative_quantity_rejected(services):
    inv = services["inventory"]
    sales = services["sales"]

    p = inv.create_product(
        name="Vitamina C",
        generic_name="Ácido Ascórbico",
        product_code="MED-VIT-01",
        description="Vitamina",
        stock=50,
        presentation="Frasco",
        laboratory="Calox",
        expiration_date="2028-01-01",
        dose="500mg",
        cost_price=5.0,
        sale_price=8.0
    )

    with pytest.raises(ValueError, match="mayor a cero"):
        sales.create_sale(
            items_data=[{"product_id": p.id, "quantity": -3}]
        )
