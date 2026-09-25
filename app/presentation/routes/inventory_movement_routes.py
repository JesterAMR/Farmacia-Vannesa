from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.presentation.routes.auth import login_required
from app.application.services.inventory_movement_service import InventoryMovementService
from app.application.services.inventory_service import InventoryService
from app.application.services.audit_service import AuditService

def create_inventory_movement_blueprint(movement_service: InventoryMovementService, 
                                        inventory_service: InventoryService,
                                        audit_service: AuditService) -> Blueprint:
    bp = Blueprint('inventory_movements', __name__, url_prefix='/inventory/movements')

    @bp.route('/', methods=['GET', 'POST'])
    @login_required
    def index():
        if request.method == 'POST':
            prod_param = request.form.get('product_name', '').strip()
            movement_type = request.form.get('type', 'Entrada')
            quantity_str = request.form.get('quantity', '1')
            reason = request.form.get('reason', 'Ajuste operativo')
            notes = request.form.get('notes', '')

            try:
                quantity = int(quantity_str)
            except ValueError:
                quantity = 1

            # Resolver producto por ID o Nombre
            product = None
            if prod_param.isdigit():
                product = inventory_service.get_product(int(prod_param))
            
            if not product and prod_param:
                for p in inventory_service.get_all_products(include_inactive=True):
                    if p.name.strip().lower() == prod_param.lower() or p.product_code.strip().lower() == prod_param.lower():
                        product = p
                        break

            if not product:
                flash(f'Error: No se encontró el medicamento "{prod_param}".', 'error')
                return redirect(url_for('inventory_movements.index'))

            user_id = session.get('user_id')
            try:
                mov = movement_service.register_movement(
                    product_id=product.id,
                    movement_type=movement_type,
                    quantity=quantity,
                    reason=reason,
                    notes=notes,
                    user_id=user_id
                )
                audit_service.log_action(
                    action=f"Registró Movimiento de Inventario ({movement_type})",
                    user_id=user_id,
                    details=f"Medicamento: {product.name} ({quantity} unid.) - Motivo: {reason}"
                )
                flash(f'Movimiento registrado: {movement_type} de {quantity} unidades para "{product.name}" ({reason}).', 'success')
            except ValueError as e:
                flash(str(e), 'error')
            except Exception as e:
                flash(f'Error al registrar movimiento: {e}', 'error')

            return redirect(url_for('inventory_movements.index'))

        # Obtener lista real de movimientos
        raw_movements = movement_service.get_all_movements(limit=100)
        movements_list = []
        for m in raw_movements:
            movements_list.append({
                "id": f"MOV-{m.id:04d}",
                "timestamp": m.created_at,
                "product_code": m.product_code or f"MED-{m.product_id:03d}",
                "product_name": m.product_name or "Medicamento",
                "presentation": m.presentation or "Estándar",
                "type": m.movement_type,
                "quantity": m.quantity,
                "previous_stock": m.previous_stock,
                "new_stock": m.new_stock,
                "reason": m.reason,
                "user": m.username or "admin",
                "badge_class": m.badge_class
            })

        # Métricas calculadas reales
        metrics = movement_service.get_metrics()

        # Productos para el select modal
        catalog_products = inventory_service.get_all_products()
        products_for_select = [
            {"id": p.id, "name": p.name, "code": p.product_code, "stock": p.stock}
            for p in catalog_products
        ]

        return render_template('inventory_movements.html',
                               movements_list=movements_list,
                               metrics=metrics,
                               products=products_for_select)

    return bp
