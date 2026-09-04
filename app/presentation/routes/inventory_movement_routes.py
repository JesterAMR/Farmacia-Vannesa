from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.presentation.routes.auth import login_required
from datetime import datetime

def create_inventory_movement_blueprint() -> Blueprint:
    bp = Blueprint('inventory_movements', __name__, url_prefix='/inventory/movements')

    @bp.route('/', methods=['GET', 'POST'])
    @login_required
    def index():
        if request.method == 'POST':
            prod_name = request.form.get('product_name', 'Medicamento')
            movement_type = request.form.get('type', 'Entrada')
            quantity = request.form.get('quantity', '1')
            reason = request.form.get('reason', 'Ajuste operativo')

            flash(f'Movimiento registrado: {movement_type} de {quantity} unidades para "{prod_name}" ({reason}).', 'success')
            return redirect(url_for('inventory_movements.index'))

        # Mock data de movimientos de inventario (Kardex)
        movements_list = [
            {
                "id": "MOV-0052",
                "timestamp": "2026-09-03 10:15",
                "product_code": "MED-001",
                "product_name": "Paracetamol 500mg",
                "presentation": "Caja 20 Tabletas",
                "type": "Entrada",
                "quantity": 100,
                "previous_stock": 50,
                "new_stock": 150,
                "reason": "Compra Factura #F-8842",
                "user": "admin",
                "badge_class": "badge-entry"
            },
            {
                "id": "MOV-0051",
                "timestamp": "2026-09-03 09:42",
                "product_code": "MED-002",
                "product_name": "Amoxicilina 500mg",
                "presentation": "Frasco Suspensión",
                "type": "Salida",
                "quantity": -2,
                "previous_stock": 25,
                "new_stock": 23,
                "reason": "Venta en Mostrador #V-142",
                "user": "cajero1",
                "badge_class": "badge-exit"
            },
            {
                "id": "MOV-0050",
                "timestamp": "2026-09-02 18:20",
                "product_code": "MED-004",
                "product_name": "Ibuprofeno 400mg",
                "presentation": "Caja 30 Cápsulas",
                "type": "Ajuste / Merma",
                "quantity": -5,
                "previous_stock": 38,
                "new_stock": 33,
                "reason": "Producto Vencido / Descarte",
                "user": "admin",
                "badge_class": "badge-adj"
            },
            {
                "id": "MOV-0049",
                "timestamp": "2026-09-02 16:11",
                "product_code": "MED-005",
                "product_name": "Loratadina 10mg",
                "presentation": "Caja 10 Tabletas",
                "type": "Salida",
                "quantity": -4,
                "previous_stock": 18,
                "new_stock": 14,
                "reason": "Venta en Mostrador #V-139",
                "user": "cajero1",
                "badge_class": "badge-exit"
            },
            {
                "id": "MOV-0048",
                "timestamp": "2026-09-02 11:30",
                "product_code": "MED-008",
                "product_name": "Omeprazol 20mg",
                "presentation": "Caja 28 Cápsulas",
                "type": "Entrada",
                "quantity": 50,
                "previous_stock": 12,
                "new_stock": 62,
                "reason": "Recepción Proveedor DIMEG",
                "user": "admin",
                "badge_class": "badge-entry"
            },
            {
                "id": "MOV-0047",
                "timestamp": "2026-09-01 15:45",
                "product_code": "MED-012",
                "product_name": "Alcohol Antiséptico 70% 500ml",
                "presentation": "Botella",
                "type": "Ajuste / Merma",
                "quantity": -1,
                "previous_stock": 15,
                "new_stock": 14,
                "reason": "Frasco dañado en manipulación",
                "user": "admin",
                "badge_class": "badge-adj"
            },
            {
                "id": "MOV-0046",
                "timestamp": "2026-09-01 14:10",
                "product_code": "MED-003",
                "product_name": "Salbutamol Inhalador 100mcg",
                "presentation": "Inhalador 200 dosis",
                "type": "Entrada",
                "quantity": 1,
                "previous_stock": 7,
                "new_stock": 8,
                "reason": "Devolución Cliente (Envase sellado)",
                "user": "admin",
                "badge_class": "badge-entry"
            },
            {
                "id": "MOV-0045",
                "timestamp": "2026-09-01 10:05",
                "product_code": "MED-015",
                "product_name": "Acetaminofén Jarabe 120ml",
                "presentation": "Frasco Jarabe",
                "type": "Salida",
                "quantity": -3,
                "previous_stock": 30,
                "new_stock": 27,
                "reason": "Venta en Mostrador #V-135",
                "user": "cajero1",
                "badge_class": "badge-exit"
            },
            {
                "id": "MOV-0044",
                "timestamp": "2026-08-31 17:30",
                "product_code": "MED-020",
                "product_name": "Complejo B Inyectable",
                "presentation": "Ampolla 10ml",
                "type": "Ajuste / Merma",
                "quantity": 3,
                "previous_stock": 22,
                "new_stock": 25,
                "reason": "Ajuste positivo por Arqueo Físico",
                "user": "admin",
                "badge_class": "badge-entry"
            }
        ]

        # Métricas de resumen
        metrics = {
            "total_movements": len(movements_list),
            "total_entries": 154,
            "total_exits": 9,
            "total_losses": 6
        }

        # Mock de catálogo de productos para el modal de nuevo movimiento
        sample_products = [
            {"code": "MED-001", "name": "Paracetamol 500mg", "stock": 150},
            {"code": "MED-002", "name": "Amoxicilina 500mg", "stock": 23},
            {"code": "MED-003", "name": "Salbutamol Inhalador", "stock": 8},
            {"code": "MED-004", "name": "Ibuprofeno 400mg", "stock": 33},
            {"code": "MED-005", "name": "Loratadina 10mg", "stock": 14},
            {"code": "MED-008", "name": "Omeprazol 20mg", "stock": 62},
            {"code": "MED-012", "name": "Alcohol Antiséptico 70%", "stock": 14}
        ]

        return render_template('inventory_movements.html',
                               movements=movements_list,
                               metrics=metrics,
                               products=sample_products)

    return bp
