from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.presentation.routes.auth import login_required
from app.infrastructure.repositories.supabase_inventory_movement_repository import SupabaseInventoryMovementRepository
from app.application.services.inventory_service import InventoryService
from app.application.services.audit_service import AuditService
from datetime import datetime
from typing import Optional

def create_inventory_movement_blueprint(inv_mov_repo: Optional[SupabaseInventoryMovementRepository] = None,
                                        inventory_service: Optional[InventoryService] = None,
                                        audit_service: Optional[AuditService] = None) -> Blueprint:
    bp = Blueprint('inventory_movements', __name__, url_prefix='/inventory/movements')
    repo = inv_mov_repo or SupabaseInventoryMovementRepository()

    @bp.route('/', methods=['GET', 'POST'])
    @login_required
    def index():
        user_id = session.get('user_id')

        if request.method == 'POST':
            product_id_str = request.form.get('product_id')
            movement_type = request.form.get('type', 'Entrada')
            qty_str = request.form.get('quantity', '1')
            reason = request.form.get('reason', 'Ajuste operativo')
            notes = request.form.get('notes', '')

            try:
                product_id = int(product_id_str)
                quantity = int(qty_str)
                if quantity <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                flash('Cantidad o producto inválido.', 'error')
                return redirect(url_for('inventory_movements.index'))

            # Obtener el producto de Supabase
            product = None
            if inventory_service:
                product = inventory_service.get_product(product_id)

            if not product:
                flash('Medicamento no encontrado en el inventario.', 'error')
                return redirect(url_for('inventory_movements.index'))

            prev_stock = product.stock

            if movement_type == 'Entrada':
                product.stock += quantity
                signed_qty = quantity
            else: # Salida o Ajuste / Merma
                if product.stock < quantity:
                    flash(f'Stock insuficiente para "{product.name}". Existencias actuales: {product.stock} unid.', 'error')
                    return redirect(url_for('inventory_movements.index'))
                product.stock -= quantity
                signed_qty = -quantity

            # Actualizar stock en Supabase (tabla products)
            if inventory_service:
                inventory_service.update_product(product)

            # Insertar movimiento en Supabase (tabla inventory_movements)
            repo.add_movement({
                "product_id": product.id,
                "user_id": user_id,
                "movement_type": movement_type,
                "quantity": signed_qty,
                "previous_stock": prev_stock,
                "new_stock": product.stock,
                "reason": reason,
                "notes": notes,
                "created_at": datetime.now().isoformat()
            })

            # Registrar en auditoría
            if audit_service:
                audit_service.log_action(
                    action=f"Movimiento Inventario: {movement_type}",
                    user_id=user_id,
                    details=f"{product.name} ({signed_qty:+d} unid.). Stock previo: {prev_stock} -> Final: {product.stock}. Motivo: {reason}"
                )

            flash(f'¡Movimiento guardado en Supabase! {movement_type} de {quantity} unidades para "{product.name}". Nuevo stock: {product.stock}.', 'success')
            return redirect(url_for('inventory_movements.index'))

        # Consultar movimientos reales de Supabase
        raw_movements = repo.get_all_movements(limit=50)
        metrics = repo.get_metrics()

        formatted_movements = []
        for m in raw_movements:
            c_date = (m.get('created_at') or '').replace('T', ' ')[:16]
            formatted_movements.append({
                "id": f"MOV-{m.get('id', 0):04d}",
                "timestamp": c_date,
                "product_code": m.get('product_code', 'N/A'),
                "product_name": m.get('product_name', 'Medicamento'),
                "presentation": m.get('presentation', ''),
                "type": m.get('movement_type', 'Ajuste'),
                "quantity": m.get('quantity', 0),
                "previous_stock": m.get('previous_stock', 0),
                "new_stock": m.get('new_stock', 0),
                "reason": m.get('reason', 'General'),
                "user": m.get('username') or 'admin',
                "badge_class": m.get('badge_class', 'badge-adj')
            })

        # Obtener catálogo de productos activos de Supabase para el selector
        products_list = []
        if inventory_service:
            products_list = inventory_service.get_all_products(include_inactive=False)

        return render_template('inventory_movements.html',
                               movements=formatted_movements,
                               metrics=metrics,
                               products=products_list)

    return bp
