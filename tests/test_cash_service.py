import pytest

def test_cash_shift_lifecycle(services):
    cash = services["cash"]

    # 1. Apertura de turno
    shift = cash.open_shift(
        cashier="cajero_juan",
        shift_name="Matutino",
        initial_amount=1500.0,
        notes="Fondo base matutino"
    )
    assert shift.id is not None
    assert shift.status == "Abierta"
    assert shift.initial_amount == 1500.0

    # 2. Intentar abrir otro turno mientras uno está abierto debe fallar
    with pytest.raises(ValueError, match="Ya existe un turno abierto"):
        cash.open_shift(cashier="cajero_dos", shift_name="Vespertino", initial_amount=1000.0)

    # 3. Registrar egreso operativo
    mov = cash.add_movement(
        movement_type="Egreso",
        concept="Compra de agua purificada para personal",
        amount=150.0,
        voucher="REC-01"
    )
    assert mov.id is not None

    # 4. Registrar ingreso extraordinario
    mov2 = cash.add_movement(
        movement_type="Ingreso",
        concept="Reembolso de transporte",
        amount=50.0
    )
    assert mov2.id is not None

    # 5. Resumen financiero
    summary = cash.get_financial_summary(shift_id=shift.id)
    # Esperado: 1500 (fondo) + 50 (ingreso) - 150 (egreso) = 1400.0
    assert summary["current_drawer"] == 1400.0

    # 6. Cierre de caja con cuadre exacto (1400.0)
    closed = cash.close_shift(physical_cash=1400.0, notes="Cuadre perfecto")
    assert closed.status == "Cerrada"
    assert closed.difference == 0.0

    # 7. Ya no hay turno abierto
    assert cash.get_open_shift() is None
