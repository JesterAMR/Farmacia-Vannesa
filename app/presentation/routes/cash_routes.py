from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.presentation.routes.auth import login_required
from app.application.services.cash_service import CashService
from app.application.services.audit_service import AuditService
from datetime import datetime

def create_cash_blueprint(cash_service: CashService, audit_service: AuditService) -> Blueprint:
    bp = Blueprint('cash', __name__, url_prefix='/cash')

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

            user_id = session.get('user_id')
            try:
                new_shift = cash_service.open_shift(
                    cashier=cashier,
                    shift_name=shift,
                    initial_amount=initial_amount,
                    notes=notes,
                    user_id=user_id
                )
                audit_service.log_action(
                    action="Registró Apertura de Caja",
                    user_id=user_id,
                    details=f"Turno: {shift}, Fondo inicial: C${initial_amount:.2f}"
                )
                flash(f'¡Apertura de caja registrada con éxito! Turno: {shift}, Fondo inicial: C${initial_amount:.2f}', 'success')
            except ValueError as e:
                flash(str(e), 'error')
            except Exception as e:
                flash(f'Error al registrar apertura: {e}', 'error')

            return redirect(url_for('cash.open_cash'))

        # Consultar turnos reales
        raw_shifts = cash_service.get_recent_shifts(limit=10)
        recent_openings = []
        for s in raw_shifts:
            recent_openings.append({
                "id": s.id,
                "date": s.opened_at,
                "cashier": s.cashier_username or "Cajero",
                "shift": s.shift_name,
                "register": s.register_name,
                "initial_amount": s.initial_amount,
                "status": f"{s.status} ({'En curso' if s.status == 'Abierta' else 'Cerrada'})"
            })

        return render_template('cash_open.html', 
                               current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                               recent_openings=recent_openings,
                               denominations=denominations)

    @bp.route('/close', methods=['GET', 'POST'])
    @login_required
    def close_cash():
        if request.method == 'POST':
            physical_total_str = request.form.get('physical_total', '0')
            notes = request.form.get('notes', '')
            try:
                physical_total = float(physical_total_str)
            except ValueError:
                physical_total = 0.0

            user_id = session.get('user_id')
            try:
                closed_shift = cash_service.close_shift(physical_cash=physical_total, notes=notes)
                diff = closed_shift.difference if closed_shift else 0.0
                
                status_txt = "Cuadre Exacto" if diff == 0 else ("Sobrante" if diff > 0 else "Faltante")
                audit_service.log_action(
                    action="Registró Cierre de Caja",
                    user_id=user_id,
                    details=f"Total Físico: C${physical_total:.2f}, {status_txt}: C${abs(diff):.2f}"
                )

                if diff == 0:
                    flash(f'¡Arqueo y Cierre de caja completado! Cuadre exacto con C${physical_total:.2f}.', 'success')
                elif diff > 0:
                    flash(f'Cierre registrado con sobrante de C${diff:.2f}. Total físico: C${physical_total:.2f}.', 'success')
                else:
                    flash(f'Cierre registrado con faltante de C${abs(diff):.2f}. Total físico: C${physical_total:.2f}.', 'error')
            except ValueError as e:
                flash(str(e), 'error')
            except Exception as e:
                flash(f'Error al registrar cierre: {e}', 'error')

            return redirect(url_for('cash.close_cash'))

        # Datos del turno activo
        open_shift = cash_service.get_open_shift()
        if open_shift:
            fin_summary = cash_service.get_financial_summary(shift_id=open_shift.id)
            shift_summary = {
                "initial_cash": open_shift.initial_amount,
                "cash_sales": fin_summary.get("total_income", 0.0),
                "card_sales": 0.0,
                "transfer_sales": 0.0,
                "total_sales": fin_summary.get("total_income", 0.0),
                "expected_cash": fin_summary.get("current_drawer", open_shift.initial_amount),
                "cashier": open_shift.cashier_username or session.get('username', 'Cajero'),
                "shift": open_shift.shift_name,
                "opened_at": open_shift.opened_at,
                "closed_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        else:
            shift_summary = {
                "initial_cash": 0.0,
                "cash_sales": 0.0,
                "card_sales": 0.0,
                "transfer_sales": 0.0,
                "total_sales": 0.0,
                "expected_cash": 0.0,
                "cashier": session.get('username', 'Cajero'),
                "shift": "Sin turno activo",
                "opened_at": "--:--",
                "closed_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

        # Cierres recientes
        all_shifts = cash_service.get_recent_shifts(limit=15)
        recent_closings = []
        for s in all_shifts:
            if s.status == "Cerrada":
                diff = s.difference or 0.0
                status_label = "Cuadre Exacto" if diff == 0 else ("Sobrante" if diff > 0 else "Faltante")
                recent_closings.append({
                    "date": s.closed_at or s.opened_at,
                    "cashier": s.cashier_username or "Cajero",
                    "shift": s.shift_name,
                    "expected": s.expected_cash or s.initial_amount,
                    "counted": s.physical_cash or 0.0,
                    "difference": diff,
                    "status": status_label
                })

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
            try:
                amount = float(request.form.get('amount', '0') or 0)
            except ValueError:
                amount = 0.0
            concept = request.form.get('concept', 'Movimiento de caja')
            voucher = request.form.get('voucher', '')

            user_id = session.get('user_id')
            try:
                cash_service.add_movement(
                    movement_type=m_type,
                    concept=concept,
                    amount=amount,
                    category="Operativo",
                    voucher=voucher,
                    user_id=user_id
                )
                audit_service.log_action(
                    action=f"Registró {m_type} de Caja",
                    user_id=user_id,
                    details=f"Monto: C${amount:.2f}, Concepto: {concept}"
                )
                flash(f'{m_type} registrado correctamente por monto de C${amount:.2f}: {concept}.', 'success')
            except ValueError as e:
                flash(str(e), 'error')
            except Exception as e:
                flash(f'Error al registrar movimiento: {e}', 'error')

            return redirect(url_for('cash.movements'))

        # Obtener movimientos reales de la base de datos
        raw_movements = cash_service.get_movements(limit=100)
        movements_data = []
        for m in raw_movements:
            movements_data.append({
                "id": f"CAJ-{m.id:04d}",
                "date": m.created_at,
                "type": m.movement_type,
                "category": m.category,
                "concept": m.concept,
                "amount": m.amount,
                "cashier": m.username or "Sistema",
                "voucher": m.voucher_reference or "N/A"
            })

        # Totales financieros reales
        fin_totals = cash_service.get_financial_summary()

        return render_template('cash_movements.html', 
                               movements=movements_data,
                               totals=fin_totals)

    return bp
