# -*- coding: utf-8 -*-
"""
Script generador del Informe Oficial en Word (.docx) y PDF (.pdf):
'Informe Detallado de Requisitos Legales y Normativos para Farmacias en Nicaragua
y Parámetros Técnicos para Sistemas de Facturación (MINSA / DGI)'
Farmacia Vannesa — Sistema de Gestión Farmacéutica e Inventarios
"""

import os
import sys
import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from docx_helpers import set_cell_background, set_cell_margins, set_table_borders, add_callout

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

NAVY_HEX = "1B365D"
BLUE_HEX = "2563EB"
LIGHT_BG_HEX = "F1F5F9"
ALT_ROW_HEX = "F8FAFC"

NAVY_RGB = RGBColor(0x1B, 0x36, 0x5D)
BLUE_RGB = RGBColor(0x25, 0x63, 0xEB)
DARK_RGB = RGBColor(0x1E, 0x29, 0x3B)
MUTED_RGB = RGBColor(0x64, 0x74, 0x8B)
GREEN_RGB = RGBColor(0x10, 0xB9, 0x81)
RED_RGB = RGBColor(0xEF, 0x44, 0x44)
AMBER_RGB = RGBColor(0xF5, 0x9E, 0x0B)

# ==============================================================================
# 1. GENERACIÓN DEL DOCUMENTO WORD (.DOCX)
# ==============================================================================
def generate_docx():
    docx_path = os.path.join(BASE_DIR, "Informe_Requisitos_Legales_y_Normativos_Farmacia_Nicaragua.docx")
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("FARMACIA VANNESA | MARCO LEGAL Y NORMATIVO DE FARMACIAS EN NICARAGUA")
        hrun.font.name = 'Calibri'
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        frun1 = fp.add_run("Cumplimiento Regulatorio Sanitario (MINSA Ley 292) y Fiscal (DGI Ley 822)")
        frun1.font.name = 'Calibri'
        frun1.font.size = Pt(8)
        frun1.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
        frun2 = fp.add_run("                   Documento Técnico Oficial — Edición Octubre 2026")
        frun2.font.name = 'Calibri'
        frun2.font.size = Pt(8)
        frun2.font.italic = True
        frun2.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(9.5)
    normal_style.font.color.rgb = DARK_RGB

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(13)
        run.bold = True
        run.font.color.rgb = NAVY_RGB
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(10.5)
        run.bold = True
        run.font.color.rgb = BLUE_RGB
        return p

    def add_p(text, bold_prefix=None, space_after=3):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.color.rgb = NAVY_RGB
        r_text = p.add_run(text)
        r_text.font.color.rgb = DARK_RGB
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.color.rgb = NAVY_RGB
        r_text = p.add_run(text)
        r_text.font.color.rgb = DARK_RGB
        return p

    # --- PORTADA ---
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(14)
    title_p.paragraph_format.space_after = Pt(2)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_org = title_p.add_run("FARMACIA VANNESA — GESTIÓN FARMACÉUTICA INTEGRAL")
    r_org.font.name = 'Calibri'
    r_org.font.size = Pt(11)
    r_org.bold = True
    r_org.font.color.rgb = BLUE_RGB

    main_title_p = doc.add_paragraph()
    main_title_p.paragraph_format.space_before = Pt(2)
    main_title_p.paragraph_format.space_after = Pt(4)
    main_title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = main_title_p.add_run("INFORME DE REQUISITOS LEGALES Y NORMATIVOS PARA FARMACIAS EN NICARAGUA")
    r_title.font.name = 'Calibri'
    r_title.font.size = Pt(17)
    r_title.bold = True
    r_title.font.color.rgb = NAVY_RGB

    sub_title_p = doc.add_paragraph()
    sub_title_p.paragraph_format.space_before = Pt(2)
    sub_title_p.paragraph_format.space_after = Pt(12)
    sub_title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = sub_title_p.add_run("Marco Sanitario (MINSA / ANRS), Régimen Tributario (DGI Ley 822) e Implementación en el Sistema Web")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(10)
    r_sub.italic = True
    r_sub.font.color.rgb = MUTED_RGB

    # Metadatos
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(meta_table, color="B0C4DE", sz="6")

    meta_data = [
        ("País y Jurisdicción:", "República de Nicaragua (Legislación Nacional)"),
        ("Entidades Reguladoras:", "Ministerio de Salud (MINSA), ANRS y Dirección General de Ingresos (DGI)"),
        ("Sistema Analizado e Implementado:", "Sistema Web Farmacia Vannesa (Arquitectura Python / Flask / SQLite / Supabase)"),
        ("Objetivo del Informe:", "Establecer la base normativa y acreditar el cumplimiento técnico en el sistema"),
        ("Fecha de Publicación:", "Octubre 2026 | Versión 2.0 (Conforme a Ley 292 y Ley 822)")
    ]

    col_widths = [Inches(2.5), Inches(4.5)]
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width, c1.width = col_widths[0], col_widths[1]
        set_cell_background(c0, LIGHT_BG_HEX)
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.color.rgb = NAVY_RGB
        r0.font.size = Pt(8.5)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    add_callout(doc, "PROPÓSITO Y OBLIGATORIEDAD DEL MARCO LEGAL",
                "En Nicaragua, un sistema informático para farmacias no puede concebirse únicamente como un punto de venta convencional. Debe funcionar como una herramienta de cumplimiento normativo y control de calidad bajo la responsabilidad científica del Regente Farmacéutico y las disposiciones del Ministerio de Salud (MINSA) y la Dirección General de Ingresos (DGI).")

    # --- 1. REQUISITOS SANITARIOS PARA OPERAR UNA FARMACIA EN NICARAGUA ---
    add_h1("1. Requisitos Sanitarios para la Habilitación y Operación (MINSA / ANRS)")
    add_p("El funcionamiento de un establecimiento farmacéutico en Nicaragua se rige fundamentalmente por la Ley N°. 292 ('Ley de Medicamentos y Farmacias') y su Decreto Ejecutivo N°. 19-99. Sus pilares obligatorios son:")

    add_bullet("Permiso otorgado por la Dirección de Farmacia del MINSA tras inspección higiénico-sanitaria. Tiene una vigencia improrrogable de dos (2) años (Decreto 19-99, Art. 64) y requiere presentación de escritura de constitución, poderes, RUC y solvencias.", "Licencia Sanitaria de Funcionamiento: ")
    add_bullet("Presencia indispensable de un profesional farmacéutico (Licenciado en Farmacia o Químico Farmacéutico colegiado y acreditado ante el MINSA, Ley 292 Art. 67-69). Es el responsable técnico-científico del establecimiento. Su ausencia injustificada amerita el cierre técnico inmediato de la farmacia.", "Regencia Farmacéutica Obligatoria: ")
    add_bullet("Todo fármaco comercializado debe poseer un número de Registro Sanitario expedido por el MINSA con vigencia quinquenal (5 años) y refrendos periódicos. La venta de productos sin registro constituye delito contra la salud pública.", "Registro Sanitario de Medicamentos: ")
    add_bullet("Obligación legal del regente de inspeccionar lotes, condiciones de almacenamiento (temperatura/humedad) y retirar de circulación todo lote caducado o en mal estado (Ley 292 Art. 75).", "Control de Lotes y Fechas de Vencimiento: ")
    add_bullet("Registro riguroso y foliado de compras y ventas de estupefacientes y psicotrópicos. Su dispensación exige receta médica retenida con nombre del médico, código MINSA, fecha y cédula del paciente.", "Control de Sustancias Controladas y Psicotrópicos: ")
    add_bullet("Horario mínimo ininterrumpido de 8 horas diarias y obligatoriedad de cumplir turnos de guardia nocturnos y en días feriados que establezca el MINSA distrital (Decreto 19-99 Art. 66).", "Horarios y Turnos de Guardia: ")
    add_bullet("Gestión de permisos de importación a través de la Ventanilla Única de Comercio Exterior de Nicaragua (VUCEN), con registros sanitarios previos y facturas de distribuidoras autorizadas.", "Cadena de Abastecimiento y VUCEN: ")

    # --- 2. PARÁMETROS TÉCNICOS PARA SISTEMAS INFORMÁTICOS DE FACTURACIÓN (DGI) ---
    add_h1("2. Parámetros Técnicos para Sistemas de Facturación y POS (DGI / Ley 822)")
    add_p("La Dirección General de Ingresos (DGI) regula la emisión de comprobantes fiscales electrónicos y la determinación de impuestos conforme a la Ley N°. 822 ('Ley de Concertación Tributaria - LCT'):")

    add_bullet("RUC activo del emisor (Farmacia Vannesa S.A.), Razón Social, Licencia Sanitaria, dirección fiscal y Cédula o RUC del cliente (indispensable para validez fiscal o compras corporativas).", "Identificación Tributaria Completa: ")
    add_bullet("Conforme al Artículo 153 de la Ley 822 y canasta de salud, los medicamentos de consumo humano se encuentran EXENTOS del IVA (0%). Por el contrario, los productos cosméticos, artículos de higiene y suplementos pagan la tarifa general del 15%. El sistema debe calcular y desglosar por separado: Subtotal Exento, Subtotal Gravado y el monto exacto de IVA (15%).", "Desglose Fiscal de IVA (15% vs Exento): ")
    add_bullet("Generación de archivo XML normalizado bajo las especificaciones de la DGI, estructura de datos en nodos jerárquicos (<Encabezado>, <Emisor>, <Receptor>, <DetalleArticulos>, <TotalesImpuestos>) y preparación para firma electrónica digital.", "Facturación Electrónica (Estándar XML DGI): ")
    add_bullet("Registro y cobro en Córdobas (NIO) con conversión a Dólares (USD) aplicando la tasa de cambio oficial diaria fijada por el Banco Central de Nicaragua (BCN).", "Manejo Bimonetario Oficial: ")
    add_bullet("Capacidad de almacenar transacciones con numeración reservada en contingencia local ante pérdida de conexión y transmisión diferida una vez restablecida la red.", "Resiliencia y Modo Contingencia: ")

    # --- 3. MARCO JURÍDICO CONSOLIDADO ---
    add_h1("3. Compendio Jurídico Aplicable a Farmacias en Nicaragua")
    add_p("A continuación se resumen las leyes y decretos de estricto cumplimiento para el desarrollo del software:")

    tbl_laws = doc.add_table(rows=7, cols=3)
    tbl_laws.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_laws)

    headers = ["Norma Legal", "Ámbito", "Requisitos Clave para el Sistema Informático"]
    for j, h in enumerate(headers):
        cell = tbl_laws.rows[0].cells[j]
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, 60, 60, 70, 70)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(8.5)

    laws_data = [
        ("Ley N°. 292 ('Ley de Medicamentos y Farmacias')", "Sanitario / MINSA", "Regencia obligatoria (Art. 67-69), dispensación con receta (Art. 70), sustitución por genérico (Art. 71), control de caducidad (Art. 75)."),
        ("Decreto N°. 19-99 (Reglamento de la Ley 292)", "Sanitario / MINSA", "Vigencia de 2 años de Licencia Sanitaria (Art. 64), cumplimiento de turnos de guardia obligatorios (Art. 66)."),
        ("Ley N°. 423 ('Ley General de Salud')", "Sanitario / Marco", "Garantía de calidad, inocuidad y seguridad de insumos médicos para la población."),
        ("Ley N°. 1164 ('Digesto Jurídico de Salud')", "Jurídico / Oficial", "Consolidación y vigencia de las reformas a la Ley 292 y normativas complementarias."),
        ("Ley N°. 822 ('Ley de Concertación Tributaria - LCT')", "Fiscal / DGI", "IVA general del 15% y exención de medicamentos humanos (Art. 153). Obligaciones formales del contribuyente."),
        ("Lineamientos de Facturación Electrónica DGI", "Fiscal / Técnico", "Emisión de comprobante XML normalizado, firma electrónica, serie y autorización fiscal.")
    ]

    col_w_laws = [Inches(2.0), Inches(1.2), Inches(3.8)]
    for i, (l_norm, l_amb, l_req) in enumerate(laws_data, start=1):
        row = tbl_laws.rows[i]
        bg = ALT_ROW_HEX if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate([l_norm, l_amb, l_req]):
            cell = row.cells[j]
            cell.width = col_w_laws[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 50, 50, 60, 60)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8)
            if j == 0:
                r.bold = True
                r.font.color.rgb = NAVY_RGB

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # --- 4. MATRIZ DE CUMPLIMIENTO EN FARMACIA VANNESA ---
    add_h1("4. Diagnóstico de Cumplimiento e Implementaciones en Farmacia Vannesa")
    add_p("A continuación se acredita la correspondencia entre los requisitos legales y las implementaciones técnicas realizadas en el código:")

    tbl_comp = doc.add_table(rows=9, cols=4)
    tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_comp)

    h_comp = ["Requisito Legal / Normativo", "Norma", "Estado Actual", "Evidencia Técnica en el Código"]
    for j, h in enumerate(h_comp):
        cell = tbl_comp.rows[0].cells[j]
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, 60, 60, 70, 70)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(8.5)

    comp_data = [
        ("Registro Sanitario MINSA en Medicamento", "Ley 292", "CUMPLE (Implementado)", "Campo 'sanitary_register' en Product y validación en InventoryService."),
        ("Trazabilidad de Lotes Farmacéuticos", "Decreto 19-99", "CUMPLE (Implementado)", "Campo 'batch_number' en Product, SaleItem y movimientos de Kardex."),
        ("Control de Fármacos Psicotrópicos / Receta", "Ley 292 Art. 70", "CUMPLE (Implementado)", "Bandera 'is_controlled', bloqueo automático y captura de médico prescriptor y código MINSA."),
        ("Desglose Fiscal IVA 15% vs Exento", "Ley 822 Art. 153", "CUMPLE (Implementado)", "Bandera 'is_exempt_iva', cálculo de Subtotal Exento, Subtotal Gravado e IVA en SalesService."),
        ("Manejo Bimonetario (NIO / USD)", "DGI / BCN", "CUMPLE (Implementado)", "Soporte de Córdobas (C$) y Dólares ($) con tipo de cambio oficial BCN (36.62)."),
        ("Comprobante Electrónico DGI (XML)", "DGI Técnica", "CUMPLE (Implementado)", "Generador _generate_dgi_xml() con nodo de factura electrónica y descarga directa en /invoice/<id>/xml."),
        ("Paginación Numérica en Listas", "Usabilidad / Arch", "CUMPLE (Implementado)", "Métodos get_paginated() con LIMIT/OFFSET y controles 1, 2, 3... en inventario y clientes."),
        ("Validaciones Estrictas en Base de Datos", "ISO 25010 / BD", "CUMPLE (Implementado)", "Triggers de precios positivos, stock no negativo y formato de cédula en SQLite.")
    ]

    col_w_comp = [Inches(2.2), Inches(1.1), Inches(1.4), Inches(2.3)]
    for i, (req, norm, st, evid) in enumerate(comp_data, start=1):
        row = tbl_comp.rows[i]
        bg = ALT_ROW_HEX if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate([req, norm, st, evid]):
            cell = row.cells[j]
            cell.width = col_w_comp[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 50, 50, 60, 60)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(7.5)
            if j == 0:
                r.bold = True
                r.font.color.rgb = NAVY_RGB
            elif j == 2:
                r.bold = True
                r.font.color.rgb = GREEN_RGB

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # --- 5. CONCLUSIONES Y RECOMENDACIONES ---
    add_h1("5. Conclusiones y Recomendaciones para Fase de Producción")
    add_bullet("El software cuenta con un modelo de datos plenamente alineado con la legislación sanitaria (Ley 292) y tributaria (Ley 822) de Nicaragua, asegurando la trazabilidad de los medicamentos y la transparencia fiscal.", "Arquitectura Adaptada a Nicaragua: ")
    add_bullet("Para el despliegue comercial ante la DGI en producción masiva, se recomienda conectar el generador XML existente con una API certificada de Facturación Electrónica mediante el certificado y llave digital del contribuyente.", "Firma Digital en Producción: ")
    add_bullet("El Regente Farmacéutico dispone de herramientas automatizadas para vigilar caducidades, retener recetas de psicotrópicos y justificar auditorías del MINSA.", "Soporte Operativo al Regente: ")

    doc.save(docx_path)
    print(f"[ÉXITO] Documento Word generado en: {docx_path}")
    return docx_path

# ==============================================================================
# 2. GENERACIÓN DEL DOCUMENTO PDF (.PDF)
# ==============================================================================
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawRightString(7.5 * inch, 0.45 * inch, f"FARMACIA VANNESA | Informe Legal y Normativo (Nicaragua) — Página {self._pageNumber} de {page_count}")
        self.drawString(1.0 * inch, 0.45 * inch, "Confidencial | Cumplimiento Regulatorio MINSA / DGI")
        self.restoreState()

def generate_pdf():
    pdf_path = os.path.join(BASE_DIR, "Informe_Requisitos_Legales_y_Normativos_Farmacia_Nicaragua.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleP', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=colors.HexColor("#1B365D"), alignment=1, spaceAfter=2)
    org_style = ParagraphStyle('OrgP', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor("#2563EB"), alignment=1, spaceAfter=2)
    sub_style = ParagraphStyle('SubP', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8.5, leading=11, textColor=colors.HexColor("#64748B"), alignment=1, spaceAfter=8)
    
    h1_style = ParagraphStyle('H1P', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=colors.HexColor("#1B365D"), spaceBefore=8, spaceAfter=4)
    h2_style = ParagraphStyle('H2P', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor("#2563EB"), spaceBefore=5, spaceAfter=2)
    
    body_style = ParagraphStyle('BodyP', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=10, textColor=colors.HexColor("#1E293B"), spaceAfter=3)
    bullet_style = ParagraphStyle('BullP', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.HexColor("#1E293B"), leftIndent=10, spaceAfter=2)
    
    story = []

    story.append(Paragraph("FARMACIA VANNESA — GESTIÓN FARMACÉUTICA INTEGRAL", org_style))
    story.append(Paragraph("INFORME DE REQUISITOS LEGALES Y NORMATIVOS PARA FARMACIAS EN NICARAGUA", title_style))
    story.append(Paragraph("Marco Sanitario (MINSA Ley 292), Régimen Tributario (DGI Ley 822) y Cumplimiento del Sistema Web", sub_style))

    # Tabla resumen de metadatos
    meta_pdf = [
        [Paragraph("<b>País y Jurisdicción:</b>", body_style), Paragraph("República de Nicaragua (Legislación Nacional)", body_style)],
        [Paragraph("<b>Entidades Reguladoras:</b>", body_style), Paragraph("Ministerio de Salud (MINSA), ANRS y Dirección General de Ingresos (DGI)", body_style)],
        [Paragraph("<b>Sistema Evaluado e Implementado:</b>", body_style), Paragraph("Sistema Web Farmacia Vannesa (Python / Flask / SQLite / Supabase)", body_style)],
        [Paragraph("<b>Fecha de Emisión:</b>", body_style), Paragraph("Octubre 2026 | Versión 2.0 (Conforme a Ley 292 y Ley 822)", body_style)]
    ]
    t_meta = Table(meta_pdf, colWidths=[150, 390])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#B0C4DE")),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 6))

    # 1. REQUISITOS SANITARIOS
    story.append(Paragraph("1. Requisitos Sanitarios para Operar una Farmacia en Nicaragua (MINSA / ANRS)", h1_style))
    story.append(Paragraph("• <b>Licencia Sanitaria de Funcionamiento:</b> Permiso emitido por la Dirección de Farmacia del MINSA con vigencia estricta de dos (2) años (Decreto 19-99, Art. 64).", bullet_style))
    story.append(Paragraph("• <b>Regente Farmacéutico Obligatorio:</b> Profesional titulado (Lic. en Farmacia) acreditado ante el MINSA. Es el responsable técnico legal. La farmacia no puede operar sin su supervisión (Ley 292 Art. 67-69, 75).", bullet_style))
    story.append(Paragraph("• <b>Registro Sanitario de Medicamentos:</b> Código emitido por el MINSA con vigencia de 5 años obligatorio para todo producto comercializado (Ley 292).", bullet_style))
    story.append(Paragraph("• <b>Control de Lotes y Vencimientos:</b> Obligación del regente de vigilar almacenamiento y retirar de circulación lotes caducados.", bullet_style))
    story.append(Paragraph("• <b>Control de Psicotrópicos y Estupefacientes:</b> Registro riguroso y venta exclusiva mediante receta médica retenida con código MINSA del médico prescriptor (Ley 292 Art. 70).", bullet_style))
    story.append(Paragraph("• <b>Horarios y Turnos de Guardia:</b> Mínimo 8 horas continuas diarias y cumplimiento obligatorio de turnos de noche asignados por el MINSA (Decreto 19-99 Art. 66).", bullet_style))

    # 2. PARÁMETROS TÉCNICOS DGI
    story.append(Spacer(1, 4))
    story.append(Paragraph("2. Parámetros Técnicos para Sistemas de Facturación y POS (DGI / Ley 822)", h1_style))
    story.append(Paragraph("• <b>Identificación Tributaria:</b> RUC emisor (Farmacia Vannesa), Licencia Sanitaria, dirección y Cédula/RUC del cliente (Ley 822).", bullet_style))
    story.append(Paragraph("• <b>Desglose Fiscal de IVA (15% vs Exento):</b> Medicamentos humanos están EXENTOS del IVA (Art. 153 Ley 822). Productos cosméticos y suplementos pagan 15%. El sistema debe desglosar Subtotal Exento, Subtotal Gravado e IVA 15%.", bullet_style))
    story.append(Paragraph("• <b>Facturación Electrónica (XML DGI):</b> Emisión de comprobantes XML normalizados con firma digital y numeración consecutiva autorizada.", bullet_style))
    story.append(Paragraph("• <b>Manejo Bimonetario:</b> Transacciones en Córdobas (NIO) con conversión a Dólares (USD) a la tasa oficial del Banco Central de Nicaragua (BCN).", bullet_style))

    # 3. TABLA DE MARCO JURÍDICO
    story.append(Spacer(1, 4))
    story.append(Paragraph("3. Marco Jurídico Consolidado de la República de Nicaragua", h1_style))
    laws_pdf = [
        [Paragraph("<b>Norma Legal</b>", body_style), Paragraph("<b>Ámbito</b>", body_style), Paragraph("<b>Requisitos Clave para el Sistema Informático</b>", body_style)],
        [Paragraph("<b>Ley N°. 292</b>", body_style), Paragraph("Sanitario", body_style), Paragraph("Regencia obligatoria (Art. 67-69), recetas (Art. 70), genéricos (Art. 71), control caducidad (Art. 75).", body_style)],
        [Paragraph("<b>Decreto N°. 19-99</b>", body_style), Paragraph("Sanitario", body_style), Paragraph("Vigencia 2 años Licencia Sanitaria (Art. 64), turnos de guardia obligatorios (Art. 66).", body_style)],
        [Paragraph("<b>Ley N°. 822 (LCT)</b>", body_style), Paragraph("Fiscal / DGI", body_style), Paragraph("Exención IVA de medicamentos (Art. 153), tarifa general 15% para cosméticos.", body_style)],
        [Paragraph("<b>Lineamientos DGI</b>", body_style), Paragraph("Fiscal / IT", body_style), Paragraph("Estructura XML de factura electrónica, firma digital y modo de contingencia local.", body_style)]
    ]
    t_laws = Table(laws_pdf, colWidths=[110, 70, 360])
    t_laws.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1B365D")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    for j in range(3):
        t_laws._cellvalues[0][j].style.textColor = colors.white
    story.append(t_laws)

    # 4. MATRIZ DE CUMPLIMIENTO EN FARMACIA VANNESA
    story.append(Spacer(1, 4))
    story.append(Paragraph("4. Matriz de Cumplimiento Técnico en Farmacia Vannesa", h1_style))
    comp_pdf = [
        [Paragraph("<b>Requisito Legal</b>", body_style), Paragraph("<b>Norma</b>", body_style), Paragraph("<b>Estado</b>", body_style), Paragraph("<b>Evidencia en Código</b>", body_style)],
        [Paragraph("<b>Registro Sanitario MINSA</b>", body_style), Paragraph("Ley 292", body_style), Paragraph("<font color='#10B981'><b>CUMPLE</b></font>", body_style), Paragraph("Campo 'sanitary_register' en Product y validación en InventoryService.", body_style)],
        [Paragraph("<b>Trazabilidad por Lotes</b>", body_style), Paragraph("Decreto 19-99", body_style), Paragraph("<font color='#10B981'><b>CUMPLE</b></font>", body_style), Paragraph("Campo 'batch_number' en Product, SaleItem y Kardex de movimientos.", body_style)],
        [Paragraph("<b>Control Fármacos Psicotrópicos</b>", body_style), Paragraph("Ley 292 Art. 70", body_style), Paragraph("<font color='#10B981'><b>CUMPLE</b></font>", body_style), Paragraph("Bandera 'is_controlled', validación de médico prescriptor y código MINSA.", body_style)],
        [Paragraph("<b>Desglose IVA (15% vs Exento)</b>", body_style), Paragraph("Ley 822 Art. 153", body_style), Paragraph("<font color='#10B981'><b>CUMPLE</b></font>", body_style), Paragraph("Bandera 'is_exempt_iva', cálculo de Subtotal Exento, Gravado e IVA en POS.", body_style)],
        [Paragraph("<b>Manejo Bimonetario (NIO / USD)</b>", body_style), Paragraph("DGI / BCN", body_style), Paragraph("<font color='#10B981'><b>CUMPLE</b></font>", body_style), Paragraph("Conversión automática a Dólares con tasa oficial BCN (36.62 NIO/USD).", body_style)],
        [Paragraph("<b>Factura Electrónica DGI (XML)</b>", body_style), Paragraph("DGI Técnica", body_style), Paragraph("<font color='#10B981'><b>CUMPLE</b></font>", body_style), Paragraph("Generación _generate_dgi_xml() y descarga directa en /invoice/<id>/xml.", body_style)],
        [Paragraph("<b>Paginación Numérica en Listas</b>", body_style), Paragraph("Usabilidad", body_style), Paragraph("<font color='#10B981'><b>CUMPLE</b></font>", body_style), Paragraph("Paginación con controles 1, 2, 3... en inventario y clientes.", body_style)],
        [Paragraph("<b>Validaciones Estrictas en BD</b>", body_style), Paragraph("ISO 25010", body_style), Paragraph("<font color='#10B981'><b>CUMPLE</b></font>", body_style), Paragraph("Triggers SQL para precios > 0, stock >= 0 y cédula válida.", body_style)]
    ]
    t_comp = Table(comp_pdf, colWidths=[140, 75, 75, 250])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1B365D")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    for j in range(4):
        t_comp._cellvalues[0][j].style.textColor = colors.white
    story.append(t_comp)

    # Conclusión
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Conclusión Técnica:</b> El sistema Farmacia Vannesa ha superado con éxito las pruebas unitarias y de integración, garantizando una administración farmacéutica transparente, segura y jurídicamente conforme con la República de Nicaragua.", body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[ÉXITO] Documento PDF generado en: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    generate_docx()
    generate_pdf()
