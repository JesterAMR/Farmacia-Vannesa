from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, session, Response
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
                           product_repo: ProductRepositoryInterface) -> Blueprint:
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
        return jsonify([
            {
                "id": p.id,
                "name": p.name,
                "generic_name": p.generic_name,
                "price": p.price,
                "stock": p.stock,
                "is_controlled": getattr(p, 'is_controlled', False),
                "is_exempt_iva": getattr(p, 'is_exempt_iva', True),
                "sanitary_register": getattr(p, 'sanitary_register', 'MINSA-REG-2024-001'),
                "batch_number": getattr(p, 'batch_number', 'LOT-GEN-01')
            }
            for p in products
        ])

    @bp.route('/checkout', methods=['POST'])
    @login_required
    def checkout():
        try:
            items_json = request.form.get('items')
            items_data = json.loads(items_json) if items_json else []
            
            client_id_str = request.form.get('client_id')
            client_id = int(client_id_str) if (client_id_str and client_id_str.isdigit()) else None
            
            currency = request.form.get('currency', 'NIO')
            exchange_rate = float(request.form.get('exchange_rate', 36.62))
            
            prescription_doctor = request.form.get('prescription_doctor')
            doctor_minsa_code = request.form.get('doctor_minsa_code')
            prescription_number = request.form.get('prescription_number')
            
            if not items_data:
                flash('No hay artículos en la venta', 'error')
                return redirect(url_for('sales.index'))
                
            sale = sales_service.create_sale(
                items_data,
                client_id=client_id,
                user_id=session.get('user_id'),
                currency=currency,
                exchange_rate=exchange_rate,
                prescription_doctor=prescription_doctor,
                doctor_minsa_code=doctor_minsa_code,
                prescription_number=prescription_number
            )
            
            # Registro en auditoría
            client_name = "Consumidor Final"
            if client_id:
                cl = client_service.get_client(client_id)
                if cl:
                    client_name = cl.name

            audit_service.log_action(
                action=f"Emitió Factura Fiscal #{sale.id} ({sale.dgi_auth_number})",
                user_id=session.get('user_id'),
                details=f"Cliente: {client_name}, Total: {sale.currency} {sale.total:.2f} (USD ${sale.total_usd:.2f}), Exento: C${sale.subtotal_exempt:.2f}, IVA 15%: C${sale.iva_total:.2f}"
            )
            
            flash(f'Venta #{sale.id} registrada con Factura Electrónica DGI ({sale.dgi_auth_number}). Total: {sale.currency} {sale.total:.2f}', 'success')
            return redirect(url_for('sales.invoice', id=sale.id))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f"Error al procesar la venta: {e}", 'error')
            
        return redirect(url_for('sales.index'))

    @bp.route('/invoice/<int:id>')
    @login_required
    def invoice(id: int):
        sale = sales_service.get_sale(id)
        if not sale:
            flash('Venta no encontrada', 'error')
            return redirect(url_for('sales.index'))
        
        client = None
        if sale.client_id:
            client = client_service.get_client(sale.client_id)
            
        for item in sale.items:
            product = product_repo.get_by_id(item.product_id)
            if product:
                item.product_name = product.name
                item.sanitary_register = getattr(product, 'sanitary_register', 'N/A')
            else:
                item.product_name = "Producto Desconocido"
                item.sanitary_register = "N/A"
            
        return render_template('invoice.html', sale=sale, client=client)

    @bp.route('/invoice/<int:id>/xml')
    @login_required
    def invoice_xml(id: int):
        """Descarga del archivo XML de Factura Electrónica normalizado para la DGI de Nicaragua."""
        sale = sales_service.get_sale(id)
        if not sale or not sale.fiscal_xml:
            flash('Comprobante electrónico XML no disponible para esta venta.', 'error')
            return redirect(url_for('sales.index'))

        return Response(
            sale.fiscal_xml,
            mimetype="application/xml",
            headers={"Content-Disposition": f"attachment;filename=FacturaElectronica_DGI_{sale.id:06d}.xml"}
        )

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

        # Generar PDF oficial en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor("#1b365d"),
            spaceAfter=2,
            alignment=1
        )
        
        header_style = ParagraphStyle(
            'InvoiceHeader',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#334155")
        )
        
        normal_style = ParagraphStyle(
            'InvoiceNormal',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#1e293b")
        )
        
        bold_style = ParagraphStyle(
            'InvoiceBold',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=11,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor("#1e293b")
        )

        story = []
        
        story.append(Paragraph("⚕️ FARMACIA VANNESA S.A.", title_style))
        story.append(Paragraph("<font size='9' color='#64748b'>RUC: J0310000123456 | Licencia Sanitaria MINSA: LIC-MINSA-2026-FARM-088<br/>Regente Farmacéutico Responsable: Lic. Farmacéutico Acreditado | Managua, Nicaragua</font>", ParagraphStyle('Sub', parent=title_style, alignment=1)))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<b>FACTURA ELECTRÓNICA COMERCIAL — DGI SERIE: {sale.dgi_auth_number or ('FE-2026-' + str(sale.id))}</b>", ParagraphStyle('FE', parent=bold_style, fontSize=10, textColor=colors.HexColor("#2563eb"), alignment=1)))
        story.append(Spacer(1, 8))
        
        details_data = [
            [
                Paragraph(f"<b>No. Factura:</b> {sale.id:06d}", header_style),
                Paragraph(f"<b>Cliente:</b> {client.name if client else 'Consumidor Final'}", header_style)
            ],
            [
                Paragraph(f"<b>Fecha de Emisión:</b> {sale.date.replace('T', ' ')[:19]}", header_style),
                Paragraph(f"<b>Cédula / RUC Cliente:</b> {client.identity_card if client else 'N/A'}", header_style)
            ],
            [
                Paragraph(f"<b>Moneda de Operación:</b> {sale.currency} (Tasa BCN: C${sale.exchange_rate:.4f})", header_style),
                Paragraph(f"<b>Teléfono:</b> {client.phone if (client and client.phone) else 'N/A'}", header_style)
            ]
        ]

        if sale.prescription_doctor:
            details_data.append([
                Paragraph(f"<b>Médico Prescriptor (Ley 292):</b> {sale.prescription_doctor}", header_style),
                Paragraph(f"<b>Código MINSA:</b> {sale.doctor_minsa_code or 'N/A'} | <b>Receta #:</b> {sale.prescription_number or 'N/A'}", header_style)
            ])
        
        details_table = Table(details_data, colWidths=[270, 270])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 12))
        
        table_data = [[
            Paragraph("<b>Descripción del Medicamento</b>", bold_style),
            Paragraph("<b>Reg. MINSA / Lote</b>", bold_style),
            Paragraph("<b>Cant.</b>", bold_style),
            Paragraph("<b>P. Unit (C$)</b>", bold_style),
            Paragraph("<b>Exento / Grav</b>", bold_style),
            Paragraph("<b>Subtotal (C$)</b>", bold_style)
        ]]
        
        for item in sale.items:
            product = product_repo.get_by_id(item.product_id)
            prod_name = product.name if product else "Medicamento"
            reg_lote = f"{getattr(product, 'sanitary_register', 'N/A')}<br/>{item.batch_number or 'N/A'}"
            ex_txt = "Exento (0%)" if item.is_exempt else "Gravado (15%)"
            
            table_data.append([
                Paragraph(prod_name, normal_style),
                Paragraph(reg_lote, normal_style),
                Paragraph(str(item.quantity), normal_style),
                Paragraph(f"C${item.price:.2f}", normal_style),
                Paragraph(ex_txt, normal_style),
                Paragraph(f"C${item.subtotal:.2f}", normal_style)
            ])
            
        # Desglose Fiscal DGI (Ley 822)
        table_data.append(["", "", "", "", Paragraph("<b>Subtotal Exento (Art. 153 LCT):</b>", normal_style), Paragraph(f"C${sale.subtotal_exempt:.2f}", normal_style)])
        table_data.append(["", "", "", "", Paragraph("<b>Subtotal Gravado:</b>", normal_style), Paragraph(f"C${sale.subtotal_taxable:.2f}", normal_style)])
        table_data.append(["", "", "", "", Paragraph("<b>IVA (15% DGI):</b>", normal_style), Paragraph(f"C${sale.iva_total:.2f}", normal_style)])
        table_data.append(["", "", "", "", Paragraph("<b>TOTAL FACTURA (C$):</b>", bold_style), Paragraph(f"<b>C${sale.total:.2f}</b>", bold_style)])
        table_data.append(["", "", "", "", Paragraph("<b>Equivalente USD ($):</b>", bold_style), Paragraph(f"<b>${sale.total_usd:.2f}</b>", bold_style)])
        
        items_table = Table(table_data, colWidths=[150, 110, 45, 65, 80, 90])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ('GRID', (0,0), (-1,-6), 0.5, colors.HexColor("#cbd5e1")),
            ('LINEABOVE', (4,-5), (5,-1), 0.5, colors.HexColor("#94a3b8")),
            ('LINEBELOW', (4,-2), (5,-2), 1, colors.HexColor("#0f172a")),
            ('PADDING', (0,0), (-1,-1), 4),
            ('ALIGN', (2,0), (2,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(items_table)
        
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            "<font size='7.5' color='#64748b'>DOCUMENTO EMITIDO CONFORME A LAS NORMAS TÉCNICAS DE FACTURACIÓN ELECTRÓNICA DE LA DGI Y LEY N° 822.<br/>"
            "Los medicamentos esenciales están exentos del IVA de acuerdo al Art. 153 de la Ley de Concertación Tributaria.<br/>"
            "¡Gracias por su compra en Farmacia Vannesa!</font>",
            ParagraphStyle('Footer', parent=normal_style, alignment=1)
        ))
        
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"Factura_DGI_Vannesa_{sale.id}.pdf",
            mimetype='application/pdf'
        )

    return bp
