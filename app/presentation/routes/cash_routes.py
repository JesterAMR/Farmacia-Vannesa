from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.presentation.routes.auth import login_required
from app.infrastructure.repositories.supabase_cash_repository import SupabaseCashRepository
from app.application.services.sales_service import SalesService
from app.application.services.audit_service import AuditService
from datetime import datetime
from typing import Optional

def create_cash_blueprint(cash_repo: Optional[SupabaseCashRepository] = None,
                          sales_service: Optional[SalesService] = None,
                          audit_service: Optional[AuditService] = None) -> Blueprint:
    bp = Blueprint('cash', __name__, url_prefix='/cash')
    repo = cash_repo or SupabaseCashRepository()

    denominations_list = [
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

    @bp.route('/open', methods=['GET', 'POST'])
    @login_required
    def open_cash():
        if request.method == 'POST':
            user_id = session.get('user_id')
            shift = request.form.get('shift', 'Matutino')
            initial_amount_str = request.form.get('initial_amount', '0')
            notes = request.form.get('notes', '')
            try:
                initial_amount = float(initial_amount_str)
            except ValueError:
                initial_amount = 0.0

            # Verificar si ya existe una caja abierta
            active_shift = repo.get_active_shift()
            if active_shift:
                flash(f"Aviso: Ya existía un turno abierto (#{active_shift['id']}). Se procederá con la nueva apertura.", 'warning')

            # Guardar en Supabase (cash_shifts)
            shift_payload = {
                "user_id": user_id,
                "shift_name": shift,
                "register_name": "Caja #1 - Principal",
                "initial_amount": initial_amount,
                "status": "Abierta",
                "notes": notes,
                "opened_at": datetime.now().isoformat()
            }
            new_shift = repo.open_shift(shift_payload)
            shift_id = new_shift.get('id') if new_shift else None

            # Registrar movimiento inicial de efectivo en Supabase (cash_movements)
            movement_payload = {
                "shift_id": shift_id,
                "user_id": user_id,
                "movement_type": "Ingreso",
                "category": "Fondo de Apertura",
                "concept": f"Fondo inicial asignado para apertura de turno {shift}",
                "amount": initial_amount,
                "voucher_reference": f"AP-{shift_id}" if shift_id else "AP-00"
            }
            repo.add_movement(movement_payload)

            if audit_service:
                audit_service.log_action(
                    action=f"Apertura de Caja ({shift})",
                    user_id=user_id,
                    details=f"Fondo inicial: C${initial_amount:.2f}, Turno ID: #{shift_id or 'N/A'}"
                )

            flash(f'¡Apertura de caja registrada en Supabase exitosamente! Turno: {shift}, Fondo inicial: C${initial_amount:.2f}', 'success')
            return redirect(url_for('cash.open_cash'))

        # Consultar datos reales de Supabase
        active_shift = repo.get_active_shift()
        raw_recent = repo.get_recent_shifts(limit=10)

        recent_openings = []
        for r in raw_recent:
            opened_str = r.get('opened_at') or ''
            clean_date = opened_str.replace('T', ' ')[:16] if opened_str else 'N/A'
            recent_openings.append({
                "id": r.get('id'),
                "date": clean_date,
                "cashier": r.get('username') or session.get('username', 'Cajero'),
                "shift": r.get('shift_name', 'Matutino'),
                "register": r.get('register_name', 'Caja #1 - Principal'),
                "initial_amount": float(r.get('initial_amount') or 0.0),
                "status": "Abierta (En curso)" if r.get('status') == 'Abierta' else "Cerrada"
            })

        return render_template('cash_open.html', 
                               current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                               active_shift=active_shift,
                               recent_openings=recent_openings,
                               denominations=denominations_list[:-1])

    @bp.route('/close', methods=['GET', 'POST'])
    @login_required
    def close_cash():
        active_shift = repo.get_active_shift()
        user_id = session.get('user_id')

        if request.method == 'POST':
            physical_total = float(request.form.get('physical_total', '0') or 0)
            difference = float(request.form.get('difference', '0') or 0)
            vault_deposit = float(request.form.get('vault_deposit', '0') or 0)
            remnant_cash = float(request.form.get('remnant_cash', '0') or 0)
            notes = request.form.get('notes', '')

            # Calcular el esperado real
            expected_cash = physical_total - difference

            if active_shift:
                shift_id = active_shift['id']
                repo.close_shift(shift_id, {
                    "status": "Cerrada",
                    "closed_at": datetime.now().isoformat(),
                    "expected_cash": expected_cash,
                    "physical_cash": physical_total,
                    "difference": difference,
                    "vault_deposit": vault_deposit,
                    "remnant_cash": remnant_cash,
                    "notes": notes
                })
            else:
                # Si no había turno abierto, creamos el registro cerrado directamente
                new_shift = repo.open_shift({
                    "user_id": user_id,
                    "shift_name": "Turno Extra",
                    "initial_amount": 0.0,
                    "status": "Cerrada",
                    "closed_at": datetime.now().isoformat(),
                    "expected_cash": expected_cash,
                    "physical_cash": physical_total,
                    "difference": difference,
                    "vault_deposit": vault_deposit,
                    "remnant_cash": remnant_cash,
                    "notes": notes
                })
                shift_id = new_shift.get('id') if new_shift else None

            # Si hubo retiro a bóveda, registrar movimiento en Supabase
            if vault_deposit > 0:
                repo.add_movement({
                    "shift_id": shift_id,
                    "user_id": user_id,
                    "movement_type": "Retiro Bóveda",
                    "category": "Custodia Financiera",
                    "concept": f"Depósito / Retiro a bóveda al cierre de turno #{shift_id}",
                    "amount": vault_deposit,
                    "voucher_reference": f"BOV-C{shift_id}"
                })

            if audit_service:
                audit_service.log_action(
                    action="Cierre y Arqueo de Caja",
                    user_id=user_id,
                    details=f"Esperado: C${expected_cash:.2f}, Físico: C${physical_total:.2f}, Diferencia: C${difference:.2f}"
                )

            if abs(difference) < 0.01:
                flash(f'¡Arqueo y Cierre registrado en Supabase con éxito! Cuadre exacto con C${physical_total:.2f}.', 'success')
            elif difference > 0:
                flash(f'Cierre guardado en Supabase con sobrante de +C${difference:.2f}. Total físico: C${physical_total:.2f}.', 'success')
            else:
                flash(f'Cierre guardado en Supabase con faltante de -C${abs(difference):.2f}. Total físico: C${physical_total:.2f}.', 'error')

            return redirect(url_for('cash.close_cash'))

        # Calcular totales reales de ventas desde Supabase
        initial_cash = float(active_shift.get('initial_amount') or 0.0) if active_shift else 0.0
        opened_at_str = (active_shift.get('opened_at') or '') if active_shift else ''

        cash_sales = 0.0
        card_sales = 0.0
        transfer_sales = 0.0

        if sales_service:
            try:
                all_sales = sales_service.get_all_sales()
                for s in all_sales:
                    # Sumar todas las ventas registradas
                    cash_sales += float(s.total)
            except Exception as e:
                print(f"Error computing sales for closing: {e}")

        expected_cash = initial_cash + cash_sales

        shift_summary = {
            "initial_cash": initial_cash,
            "cash_sales": cash_sales,
            "card_sales": card_sales,
            "transfer_sales": transfer_sales,
            "total_sales": cash_sales + card_sales + transfer_sales,
            "expected_cash": expected_cash,
            "cashier": active_shift.get('username') if active_shift else session.get('username', 'Cajero'),
            "shift": active_shift.get('shift_name', 'Matutino') if active_shift else "Sin turno abierto",
            "opened_at": opened_at_str.replace('T', ' ')[:16] if opened_at_str else "N/A",
            "closed_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        # Cierres anteriores de Supabase
        raw_shifts = repo.get_recent_shifts(limit=10)
        recent_closings = []
        for s in raw_shifts:
            if s.get('status') == 'Cerrada':
                c_date = (s.get('closed_at') or s.get('opened_at') or '').replace('T', ' ')[:16]
                diff = float(s.get('difference') or 0.0)
                status_label = "Cuadre Exacto" if abs(diff) < 0.01 else ("Sobrante" if diff > 0 else "Faltante")
                recent_closings.append({
                    "date": c_date,
                    "cashier": s.get('username', 'Cajero'),
                    "shift": s.get('shift_name', 'General'),
                    "expected": float(s.get('expected_cash') or 0.0),
                    "counted": float(s.get('physical_cash') or 0.0),
                    "difference": diff,
                    "status": status_label
                })

        return render_template('cash_close.html',
                               summary=shift_summary,
                               denominations=denominations_list,
                               recent_closings=recent_closings)

    @bp.route('/arqueo', methods=['GET', 'POST'])
    @login_required
    def arqueo():
        return close_cash()

    @bp.route('/movements', methods=['GET', 'POST'])
    @login_required
    def movements():
        user_id = session.get('user_id')

        if request.method == 'POST':
            m_type = request.form.get('movement_type', 'Egreso')
            amount = float(request.form.get('amount', '0') or 0)
            concept = request.form.get('concept', 'Movimiento de caja')
            voucher = request.form.get('voucher', '')

            active_shift = repo.get_active_shift()
            shift_id = active_shift.get('id') if active_shift else None

            # Determinar categoría
            category = "Gasto Operativo" if m_type == "Egreso" else ("Custodia Financiera" if "Retiro" in m_type else "Ingreso Extraordinario")

            repo.add_movement({
                "shift_id": shift_id,
                "user_id": user_id,
                "movement_type": m_type,
                "category": category,
                "concept": concept,
                "amount": amount,
                "voucher_reference": voucher
            })

            if audit_service:
                audit_service.log_action(
                    action=f"Movimiento de Caja: {m_type}",
                    user_id=user_id,
                    details=f"Concepto: {concept}, Monto: C${amount:.2f}, Comprobante: {voucher}"
                )

            flash(f'{m_type} guardado en Supabase por C${amount:.2f}: {concept}.', 'success')
            return redirect(url_for('cash.movements'))

        # Consultar movimientos reales de Supabase
        raw_movements = repo.get_all_movements(limit=50)
        summary_stats = repo.get_movements_summary()

        formatted_movements = []
        for m in raw_movements:
            c_date = (m.get('created_at') or '').replace('T', ' ')[:16]
            formatted_movements.append({
                "id": f"CAJ-{m.get('id', 0):03d}",
                "date": c_date,
                "type": m.get('movement_type', 'Ingreso'),
                "category": m.get('category', 'General'),
                "concept": m.get('concept', ''),
                "amount": float(m.get('amount') or 0.0),
                "cashier": m.get('username') or session.get('username', 'Cajero'),
                "voucher": m.get('voucher_reference') or 'S/C'
            })

        return render_template('cash_movements.html',
                               movements=formatted_movements,
                               summary_stats=summary_stats)

    return bp
