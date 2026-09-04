from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.presentation.routes.auth import login_required
from datetime import datetime

def create_cash_blueprint() -> Blueprint:
    bp = Blueprint('cash', __name__, url_prefix='/cash')

    @bp.route('/open', methods=['GET', 'POST'])
    @login_required
    def open_cash():
        if request.method == 'POST':
            cashier = request.form.get('cashier', session.get('username', 'Cajero'))
            shift = request.form.get('shift', 'Matutino')
            initial_amount_str = request.form.get('initial_amount', '0')
            notes = request.form.get('notes', '')
            try:
                initial_amount = float(initial_amount_str)
            except ValueError:
                initial_amount = 0.0

            flash(f'¡Apertura de caja registrada con éxito! Turno: {shift}, Fondo inicial: C${initial_amount:.2f}', 'success')
            return redirect(url_for('cash.open_cash'))

        # Mock data visual para aperturas recientes
        recent_openings = [
            {
                "id": 104,
                "date": datetime.now().strftime("%Y-%m-%d 07:30"),
                "cashier": session.get('username', 'admin'),
                "shift": "Matutino",
                "register": "Caja #1 - Principal",
                "initial_amount": 1500.00,
                "status": "Abierta (En curso)"
            },
            {
                "id": 103,
                "date": "2026-09-02 14:45",
                "cashier": "marvin.c",
                "shift": "Vespertino",
                "register": "Caja #1 - Principal",
                "initial_amount": 1500.00,
                "status": "Cerrada"
            },
            {
                "id": 102,
                "date": "2026-09-02 07:30",
                "cashier": "claudio.a",
                "shift": "Matutino",
                "register": "Caja #1 - Principal",
                "initial_amount": 1200.00,
                "status": "Cerrada"
            },
            {
                "id": 101,
                "date": "2026-09-01 14:40",
                "cashier": "edwin.s",
                "shift": "Vespertino",
                "register": "Caja #1 - Principal",
                "initial_amount": 1500.00,
                "status": "Cerrada"
            }
        ]

        denominations = [
            {"value": 1000, "label": "C$ 1,000", "type": "Billete"},
            {"value": 500, "label": "C$ 500", "type": "Billete"},
            {"value": 200, "label": "C$ 200", "type": "Billete"},
            {"value": 100, "label": "C$ 100", "type": "Billete"},
            {"value": 50, "label": "C$ 50", "type": "Billete"},
            {"value": 20, "label": "C$ 20", "type": "Billete"},
            {"value": 10, "label": "C$ 10", "type": "Billete / Moneda"},
            {"value": 5, "label": "C$ 5", "type": "Moneda"},
            {"value": 1, "label": "C$ 1", "type": "Moneda"}
        ]

        return render_template('cash_open.html', 
                               current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                               recent_openings=recent_openings,
                               denominations=denominations)

    @bp.route('/close', methods=['GET', 'POST'])
    @login_required
    def close_cash():
        if request.method == 'POST':
            physical_total_str = request.form.get('physical_total', '0')
            difference_str = request.form.get('difference', '0')
            notes = request.form.get('notes', '')
            try:
                physical_total = float(physical_total_str)
                diff = float(difference_str)
            except ValueError:
                physical_total = 0.0
                diff = 0.0

            if diff == 0:
                flash(f'¡Arqueo y Cierre de caja completado! Cuadre exacto con C${physical_total:.2f}.', 'success')
            elif diff > 0:
                flash(f'Cierre registrado con sobrante de C${diff:.2f}. Total físico: C${physical_total:.2f}.', 'success')
            else:
                flash(f'Cierre registrado con faltante de C${abs(diff):.2f}. Total físico: C${physical_total:.2f}.', 'error')

            return redirect(url_for('cash.close_cash'))

        # Mock resumen del turno actual
        shift_summary = {
            "initial_cash": 1500.00,
            "cash_sales": 7840.50,
            "card_sales": 3420.00,
            "transfer_sales": 1250.00,
            "total_sales": 12510.50,
            "expected_cash": 9340.50, # Fondo + ventas en efectivo
            "cashier": session.get('username', 'admin'),
            "shift": "Matutino",
            "opened_at": datetime.now().strftime("%Y-%m-%d 07:30"),
            "closed_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        # Denominaciones para el arqueo
        denominations = [
            {"value": 1000, "label": "C$ 1,000", "type": "Billete"},
            {"value": 500, "label": "C$ 500", "type": "Billete"},
            {"value": 200, "label": "C$ 200", "type": "Billete"},
            {"value": 100, "label": "C$ 100", "type": "Billete"},
            {"value": 50, "label": "C$ 50", "type": "Billete"},
            {"value": 20, "label": "C$ 20", "type": "Billete"},
            {"value": 10, "label": "C$ 10", "type": "Billete"},
            {"value": 5, "label": "C$ 5", "type": "Moneda"},
            {"value": 1, "label": "C$ 1", "type": "Moneda"},
            {"value": 0.50, "label": "C$ 0.50", "type": "Moneda"}
        ]

        recent_closings = [
            {
                "date": "2026-09-02 21:05",
                "cashier": "marvin.c",
                "shift": "Vespertino",
                "expected": 8750.00,
                "counted": 8750.00,
                "difference": 0.00,
                "status": "Cuadre Exacto"
            },
            {
                "date": "2026-09-02 14:35",
                "cashier": "claudio.a",
                "shift": "Matutino",
                "expected": 9120.00,
                "counted": 9130.00,
                "difference": 10.00,
                "status": "Sobrante"
            },
            {
                "date": "2026-09-01 21:10",
                "cashier": "edwin.s",
                "shift": "Vespertino",
                "expected": 7430.00,
                "counted": 7415.00,
                "difference": -15.00,
                "status": "Faltante"
            }
        ]

        return render_template('cash_close.html',
                               summary=shift_summary,
                               denominations=denominations,
                               recent_closings=recent_closings)

    @bp.route('/arqueo', methods=['GET', 'POST'])
    @login_required
    def arqueo():
        return close_cash()

    @bp.route('/movements', methods=['GET', 'POST'])
    @login_required
    def movements():
        if request.method == 'POST':
            m_type = request.form.get('movement_type', 'Egreso')
            amount = float(request.form.get('amount', '0') or 0)
            concept = request.form.get('concept', 'Movimiento de caja')
            voucher = request.form.get('voucher', '')
            flash(f'{m_type} registrado correctamente por monto de C${amount:.2f}: {concept}.', 'success')
            return redirect(url_for('cash.movements'))

        movements_data = [
            {
                "id": "CAJ-089",
                "date": "2026-09-03 07:30",
                "type": "Ingreso",
                "category": "Fondo de Apertura",
                "concept": "Fondo base para inicio de turno matutino",
                "amount": 1500.00,
                "cashier": "admin",
                "voucher": "AP-104"
            },
            {
                "id": "CAJ-090",
                "date": "2026-09-03 09:15",
                "type": "Ingreso",
                "category": "Ventas Mostrador",
                "concept": "Cobro acumulado ventas en efectivo período matutino",
                "amount": 4250.50,
                "cashier": "cajero1",
                "voucher": "POS-BLOQ-1"
            },
            {
                "id": "CAJ-091",
                "date": "2026-09-03 10:20",
                "type": "Egreso",
                "category": "Gasto Operativo",
                "concept": "Pago de flete recepción medicamentos droguería",
                "amount": 250.00,
                "cashier": "admin",
                "voucher": "REC-041"
            },
            {
                "id": "CAJ-092",
                "date": "2026-09-03 11:45",
                "type": "Ingreso",
                "category": "Ventas Mostrador",
                "concept": "Cobro acumulado ventas en efectivo mediodía",
                "amount": 3590.00,
                "cashier": "cajero1",
                "voucher": "POS-BLOQ-2"
            },
            {
                "id": "CAJ-093",
                "date": "2026-09-03 12:30",
                "type": "Egreso",
                "category": "Insumos",
                "concept": "Compra de rollos térmicos para impresora de tickets",
                "amount": 400.00,
                "cashier": "admin",
                "voucher": "FACT-392"
            },
            {
                "id": "CAJ-094",
                "date": "2026-09-03 13:00",
                "type": "Retiro Bóveda",
                "category": "Custodia Financiera",
                "concept": "Traslado parcial de excedente a caja fuerte / bóveda",
                "amount": 5000.00,
                "cashier": "admin",
                "voucher": "BOV-022"
            }
        ]

        return render_template('cash_movements.html', movements=movements_data)

    return bp
