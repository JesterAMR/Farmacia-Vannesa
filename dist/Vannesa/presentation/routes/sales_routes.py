from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.application.services.sales_service import SalesService
from app.application.services.inventory_service import InventoryService
from app.application.interfaces.product_repository import ProductRepositoryInterface
from app.presentation.routes.auth import login_required
import json

def create_sales_blueprint(sales_service: SalesService, inventory_service: InventoryService, product_repo: ProductRepositoryInterface) -> Blueprint:
    bp = Blueprint('sales', __name__, url_prefix='/sales')

    @bp.route('/')
    @login_required
    def index():
        products = inventory_service.get_all_products()
        sales = sales_service.get_all_sales()
        return render_template('sales.html', products=products, sales=sales)

    @bp.route('/api/products')
    @login_required
    def api_products():
        products = inventory_service.get_all_products()
        return jsonify([{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock} for p in products])

    @bp.route('/checkout', methods=['POST'])
    @login_required
    def checkout():
        try:
            items_json = request.form.get('items')
            items_data = json.loads(items_json)
            
            if not items_data:
                flash('No hay artículos en la venta', 'error')
                return redirect(url_for('sales.index'))
                
            sale = sales_service.create_sale(items_data)
            flash(f'Venta #{sale.id} registrada correctamente. Total: ${sale.total:.2f}', 'success')
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash("Error al procesar la venta", 'error')
            
        return redirect(url_for('sales.index'))

    @bp.route('/invoice/<int:id>')
    @login_required
    def invoice(id: int):
        sale = sales_service.get_sale(id)
        if not sale:
            flash('Venta no encontrada', 'error')
            return redirect(url_for('sales.index'))
        
        for item in sale.items:
            product = product_repo.get_by_id(item.product_id)
            if product:
                item.product_name = product.name
            else:
                item.product_name = "Producto Desconocido"
            
        return render_template('invoice.html', sale=sale)

    return bp
