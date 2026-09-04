from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.application.services.inventory_service import InventoryService
from app.domain.models.product import Product
from app.presentation.routes.auth import login_required, admin_required
from app.application.services.audit_service import AuditService

def create_inventory_blueprint(inventory_service: InventoryService, audit_service: AuditService) -> Blueprint:
    bp = Blueprint('inventory', __name__, url_prefix='/inventory')

    @bp.route('/')
    @login_required
    @admin_required
    def list_products():
        show_inactive = request.args.get('show_inactive', 'false') == 'true'
        products = inventory_service.get_all_products(include_inactive=show_inactive)
        return render_template('inventory.html', products=products, show_inactive=show_inactive)

    @bp.route('/add', methods=['POST'])
    @login_required
    @admin_required
    def add_product():
        name = request.form.get('name')
        generic_name = request.form.get('generic_name')
        product_code = request.form.get('product_code')
        description = request.form.get('description', '')
        stock = int(request.form.get('stock'))
        presentation = request.form.get('presentation')
        laboratory = request.form.get('laboratory')
        expiration_date = request.form.get('expiration_date')
        dose = request.form.get('dose')
        cost_price = float(request.form.get('cost_price'))
        sale_price = float(request.form.get('sale_price'))
        
        try:
            product = inventory_service.create_product(
                name, generic_name, product_code, description,
                stock, presentation, laboratory, expiration_date, dose,
                cost_price, sale_price
            )
            audit_service.log_action(
                action=f"Creó medicamento: {product.name}",
                user_id=session.get('user_id'),
                details=f"Código: {product.product_code}, Stock inicial: {product.stock}"
            )
            flash('Medicamento agregado correctamente', 'success')
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f"Error al agregar medicamento: {e}", 'error')
            
        return redirect(url_for('inventory.list_products'))

    @bp.route('/update/<int:id>', methods=['POST'])
    @login_required
    @admin_required
    def update_product(id: int):
        product = inventory_service.get_product(id)
        if product:
            product.name = request.form.get('name')
            product.generic_name = request.form.get('generic_name')
            product.product_code = request.form.get('product_code')
            product.description = request.form.get('description', '')
            product.stock = int(request.form.get('stock'))
            product.presentation = request.form.get('presentation')
            product.laboratory = request.form.get('laboratory')
            product.expiration_date = request.form.get('expiration_date')
            product.dose = request.form.get('dose')
            product.cost_price = float(request.form.get('cost_price'))
            product.sale_price = float(request.form.get('sale_price'))
            
            try:
                inventory_service.update_product(product)
                audit_service.log_action(
                    action=f"Actualizó medicamento: {product.name}",
                    user_id=session.get('user_id'),
                    details=f"ID: {product.id}, Código: {product.product_code}, Nuevo Stock: {product.stock}"
                )
                flash('Medicamento actualizado correctamente', 'success')
            except ValueError as e:
                flash(str(e), 'error')
            except Exception as e:
                flash(f"Error al actualizar medicamento: {e}", 'error')
        else:
            flash('Medicamento no encontrado', 'error')
        return redirect(url_for('inventory.list_products'))

    @bp.route('/delete/<int:id>', methods=['POST'])
    @login_required
    @admin_required
    def delete_product(id: int):
        product = inventory_service.get_product(id)
        if product:
            if inventory_service.delete_product(id):
                audit_service.log_action(
                    action=f"Desactivó medicamento: {product.name}",
                    user_id=session.get('user_id'),
                    details=f"Código: {product.product_code}"
                )
                flash('Medicamento desactivado correctamente', 'success')
            else:
                flash('No se pudo desactivar', 'error')
        else:
            flash('Medicamento no encontrado', 'error')
        return redirect(url_for('inventory.list_products'))

    @bp.route('/reactivate/<int:id>', methods=['POST'])
    @login_required
    @admin_required
    def reactivate_product(id: int):
        product = inventory_service.get_product(id)
        if product:
            product.is_active = True
            inventory_service.update_product(product)
            audit_service.log_action(
                action=f"Reactivó medicamento: {product.name}",
                user_id=session.get('user_id'),
                details=f"Código: {product.product_code}"
            )
            flash('Medicamento reactivado correctamente', 'success')
        else:
            flash('Medicamento no encontrado', 'error')
        return redirect(url_for('inventory.list_products', show_inactive=True))

    @bp.route('/restock/<int:id>', methods=['POST'])
    @login_required
    @admin_required
    def restock_product(id: int):
        added_quantity = int(request.form.get('added_quantity', 0))
        if added_quantity > 0:
            product = inventory_service.restock_product(id, added_quantity)
            if product:
                audit_service.log_action(
                    action=f"Reabasteció stock: {product.name}",
                    user_id=session.get('user_id'),
                    details=f"Cantidad agregada: +{added_quantity}, Stock final: {product.stock}"
                )
                flash(f'Inventario reabastecido (+{added_quantity}) exitosamente', 'success')
            else:
                flash('Hubo un error al reabastecer el inventario', 'error')
        else:
            flash('Cantidad debe ser mayor a 0', 'error')
        return redirect(url_for('inventory.list_products'))

    return bp
