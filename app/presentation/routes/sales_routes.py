from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from app.application.services.sales_service import SalesService
from app.application.services.inventory_service import InventoryService
from app.application.services.client_service import ClientService
from app.application.services.audit_service import AuditService
from app.application.interfaces.product_repository import ProductRepositoryInterface
from app.presentation.routes.auth import login_required
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_sales_blueprint(sales_service: SalesService, inventory_service: InventoryService, 
                           client_service: ClientService, audit_service: AuditService, 
                           product_repo: ProductRepositoryInterface,
                           inv_mov_repo = None, cash_repo = None) -> Blueprint:
    bp = Blueprint('sales', __name__, url_prefix='/sales')

    @bp.route('/')
    @login_required
    def index():
        products = inventory_service.get_all_products()
        sales = sales_service.get_all_sales()
        clients = client_service.get_all_clients()
        return render_template('sales.html', products=products, sales=sales, clients=clients)

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
            
            client_id_str = request.form.get('client_id')
            client_id = int(client_id_str) if (client_id_str and client_id_str.isdigit()) else None
            
            if not items_data:
                flash('No hay artículos en la venta', 'error')
                return redirect(url_for('sales.index'))
                
            sale = sales_service.create_sale(items_data, client_id=client_id)
            user_id = session.get('user_id')
            
            # Log action
            client_name = "Consumidor Final"
            if client_id:
                cl = client_service.get_client(client_id)
                if cl:
                    client_name = cl.name

            # Registrar movimiento de entrada de efectivo en Supabase (cash_movements)
            if cash_repo:
                try:
                    active_shift = cash_repo.get_active_shift()
                    shift_id = active_shift.get('id') if active_shift else None
                    cash_repo.add_movement({
                        "shift_id": shift_id,
                        "user_id": user_id,
                        "movement_type": "Ingreso",
                        "category": "Ventas Mostrador",
                        "concept": f"Cobro venta #{sale.id} ({client_name})",
                        "amount": sale.total,
                        "voucher_reference": f"REC-{sale.id}"
                    })
                except Exception as e:
                    print(f"Error logging cash movement on sale: {e}")

            # Registrar salida de inventario en Kardex en Supabase (inventory_movements)
            if inv_mov_repo:
                try:
                    for it in sale.items:
                        prod = product_repo.get_by_id(it.product_id)
                        current_stk = prod.stock if prod else 0
                        inv_mov_repo.add_movement({
                            "product_id": it.product_id,
                            "user_id": user_id,
                            "movement_type": "Salida",
                            "quantity": -it.quantity,
                            "previous_stock": current_stk + it.quantity,
                            "new_stock": current_stk,
                            "reason": f"Venta en Mostrador #{sale.id}"
                        })
                except Exception as e:
                    print(f"Error logging inventory movement on sale: {e}")

            audit_service.log_action(
                action=f"Registró Venta #{sale.id}",
                user_id=user_id,
                details=f"Cliente: {client_name}, Total: C${sale.total:.2f}"
            )
            
            flash(f'Venta #{sale.id} registrada correctamente en Supabase. Total: C${sale.total:.2f}', 'success')
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
        
        # Get client details
        client = None
        if sale.client_id:
            client = client_service.get_client(sale.client_id)
            
        for item in sale.items:
            product = product_repo.get_by_id(item.product_id)
            if product:
                item.product_name = product.name
            else:
                item.product_name = "Producto Desconocido"
            
        return render_template('invoice.html', sale=sale, client=client)

    @bp.route('/invoice/<int:id>/pdf')
    @login_required
    def invoice_pdf(id: int):
        sale = sales_service.get_sale(id)
        if not sale:
            flash('Venta no encontrada', 'error')
            return redirect(url_for('sales.index'))
        
        client = None
        if sale.client_id:
            client = client_service.get_client(sale.client_id)

        # Generate PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor("#3b82f6"),
            spaceAfter=5,
            alignment=1
        )
        
        header_style = ParagraphStyle(
            'InvoiceHeader',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569")
        )
        
        normal_style = ParagraphStyle(
            'InvoiceNormal',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#1e293b")
        )
        
        bold_style = ParagraphStyle(
            'InvoiceBold',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor("#1e293b")
        )

        story = []
        
        story.append(Paragraph("⚕️ FARMACIA VANNESA", title_style))
        story.append(Paragraph("<b>Comprobante Oficial de Venta</b>", ParagraphStyle('Sub', parent=title_style, fontSize=12, spaceAfter=20)))
        story.append(Spacer(1, 10))
        
        details_data = [
            [
                Paragraph(f"<b>Recibo #:</b> {sale.id}", header_style),
                Paragraph(f"<b>Cliente:</b> {client.name if client else 'Consumidor Final'}", header_style)
            ],
            [
                Paragraph(f"<b>Fecha:</b> {sale.date.replace('T', ' ')[:19]}", header_style),
                Paragraph(f"<b>Cédula/RUC:</b> {client.identity_card if client else 'N/A'}", header_style)
            ],
            [
                Paragraph("", header_style),
                Paragraph(f"<b>Teléfono:</b> {client.phone if (client and client.phone) else 'N/A'}", header_style)
            ]
        ]
        
        details_table = Table(details_data, colWidths=[240, 240])
        details_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 20))
        
        table_data = [[
            Paragraph("<b>Descripción del Medicamento</b>", bold_style),
            Paragraph("<b>Cantidad</b>", bold_style),
            Paragraph("<b>Precio Unitario</b>", bold_style),
            Paragraph("<b>Subtotal</b>", bold_style)
        ]]
        
        for item in sale.items:
            product = product_repo.get_by_id(item.product_id)
            prod_name = product.name if product else "Producto Desconocido"
            table_data.append([
                Paragraph(prod_name, normal_style),
                Paragraph(str(item.quantity), normal_style),
                Paragraph(f"C${item.price:.2f}", normal_style),
                Paragraph(f"C${item.subtotal:.2f}", normal_style)
            ])
            
        table_data.append([
            "", "",
            Paragraph("<b>Total a Pagar:</b>", bold_style),
            Paragraph(f"<b>C${sale.total:.2f}</b>", bold_style)
        ])
        
        items_table = Table(table_data, colWidths=[240, 80, 100, 80])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
            ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor("#cbd5e1")),
            ('LINEABOVE', (2,-1), (3,-1), 1, colors.HexColor("#0f172a")),
            ('PADDING', (0,0), (-1,-1), 8),
            ('ALIGN', (1,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(items_table)
        
        story.append(Spacer(1, 40))
        story.append(Paragraph("<font color='#64748b'>¡Gracias por su compra en Farmacia Vannesa!<br/>Este documento es un comprobante de pago válido.</font>", ParagraphStyle('Footer', parent=normal_style, alignment=1)))
        
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"Factura_Vannesa_{sale.id}.pdf",
            mimetype='application/pdf'
        )

    return bp
