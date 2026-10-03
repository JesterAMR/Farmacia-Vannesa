# -*- coding: utf-8 -*-
"""
Script generador del documento PDF profesional del Plan de Auditoría de Calidad
para el sistema 'Farmacia Vannesa'.
Tarea: Plan de sistemas realizados
Incorpora los 11 campos mandatorios, checklist IEEE 830, procedimientos en 2 pasos
y tabla final de mapeo integral de las 25 auditorías.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#7F8C8D"))
        
        # Header (página > 1)
        if self._pageNumber > 1:
            self.drawRightString(letter[0] - 0.75 * inch, letter[1] - 0.45 * inch,
                                 "FARMACIA VANNESA | PLAN DE AUDITORÍA INFORMÁTICA DE CALIDAD (SDLC)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(0.75 * inch, letter[1] - 0.50 * inch, letter[0] - 0.75 * inch, letter[1] - 0.50 * inch)
        
        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(0.75 * inch, 0.60 * inch, letter[0] - 0.75 * inch, 0.60 * inch)
        
        self.drawString(0.75 * inch, 0.40 * inch,
                        "Tarea: Plan de sistemas realizados | Enfoque: Calidad y Gobernanza de Software")
        self.drawRightString(letter[0] - 0.75 * inch, 0.40 * inch,
                             f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

def build_pdf():
    pdf_filename = r"c:\Proyectos\Farmacia-Vannesa\Plan_Auditoria_Calidad_Farmacia_Vannesa.pdf"
    
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.70 * inch,
        bottomMargin=0.70 * inch
    )
    
    styles = getSampleStyleSheet()
    
    c_navy = colors.HexColor("#1B365D")
    c_blue = colors.HexColor("#2B7CD3")
    c_dark = colors.HexColor("#1F2937")
    c_bg_light = colors.HexColor("#F0F4F8")
    c_alt_row = colors.HexColor("#F9FBFC")
    c_border = colors.HexColor("#D1D5DB")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=c_navy,
        alignment=1,
        spaceAfter=5
    )
    
    sub_title_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#4B5563"),
        alignment=1,
        spaceAfter=12
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=15,
        textColor=c_navy,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=c_blue,
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11.5,
        textColor=c_dark,
        spaceBefore=7,
        spaceAfter=2,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_dark,
        spaceAfter=4
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_dark,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=2.5
    )
    
    th_style = ParagraphStyle(
        'THStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=0
    )
    
    td_style = ParagraphStyle(
        'TDStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=c_dark,
        alignment=0
    )
    
    td_bold_style = ParagraphStyle(
        'TDBoldStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=c_navy,
        alignment=0
    )

    story = []
    
    # ----------------------------------------------------
    # ENCABEZADO / METADATA
    # ----------------------------------------------------
    story.append(Paragraph("FARMACIA VANNESA — SISTEMA DE GESTIÓN FARMACÉUTICA", ParagraphStyle('PreHeader', fontName='Helvetica-Bold', fontSize=9.5, leading=11, textColor=c_blue, alignment=1, spaceAfter=3)))
    story.append(Paragraph("PLAN DE AUDITORÍA INFORMÁTICA DE CALIDAD DE SISTEMAS", title_style))
    story.append(Paragraph("Programa de Trabajo Detallado de 25 Auditorías del Ciclo de Vida del Software (SDLC)<br/><b>Tarea: Plan de sistemas realizados</b>", sub_title_style))
    
    meta_data = [
        [Paragraph("<b>Organización / Cliente:</b>", td_bold_style), Paragraph("Farmacia Vannesa (Comercializadora de Productos Farmacéuticos)", td_style)],
        [Paragraph("<b>Sistema Evaluado:</b>", td_bold_style), Paragraph("Sistema Web de Control Farmacéutico e Inventarios (Farmacia Vannesa - SDLC)", td_style)],
        [Paragraph("<b>Tipo de Auditoría:</b>", td_bold_style), Paragraph("Auditoría Informática de Calidad, Estándares de Ingeniería y Gobernanza SDLC", td_style)],
        [Paragraph("<b>Alcance Metodológico:</b>", td_bold_style), Paragraph("5 Fases del Ciclo de Vida (25 Auditorías Técnicas con Procedimientos en 2 Pasos)", td_style)],
        [Paragraph("<b>Equipo Desarrollador Auditado:</b>", td_bold_style), Paragraph("Marvin Castañeda, Claudio Arana, Edwin Sevilla, Jester Mendieta", td_style)],
        [Paragraph("<b>Fecha / Versión:</b>", td_bold_style), Paragraph("Octubre 2026 | Versión 1.0 (Documento Oficial de Planificación)", td_style)]
    ]
    t_meta = Table(meta_data, colWidths=[2.2 * inch, 4.8 * inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), c_bg_light),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))
    
    callout_data = [[
        Paragraph("<b>📌 ENFOQUE EXCLUSIVO EN CALIDAD Y GOBERNANZA:</b> El presente plan evalúa las cinco (5) fases del ciclo de vida del software (SDLC): Requerimientos, Diseño, Construcción, Pruebas y Despliegue, totalizando 25 auditorías operativas. Se excluyen deliberadamente auditorías de infraestructura física (servidores on-premise, racks, UPS físicos de centros de cómputo) y redes Wi-Fi perimetrales, concentrando el rigor en la ingeniería de software y estándares ISO/IEC 25010, IEEE 830 y CMMI-DEV.", td_style)
    ]]
    t_callout = Table(callout_data, colWidths=[7.0 * inch])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('LINELEFT', (0, 0), (0, -1), 3, c_navy),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 8))

    # ----------------------------------------------------
    # 1. GOBERNANZA
    # ----------------------------------------------------
    story.append(Paragraph("1. Gobernanza de Calidad del Desarrollo del Sistema", h1_style))
    story.append(Paragraph("La Gobernanza de Calidad establece las directrices organizacionales, responsabilidades, canales de comunicación y políticas técnicas para asegurar que el sistema satisfaga los estándares internacionales. Comprende la estructura metodológica bajo la cual el equipo concibe, construye, verifica y despliega el producto.", body_style))
    story.append(Paragraph("• <b>Estructura de Roles SQA:</b> Segregación formal de funciones entre Product Owner (reglas de negocio), Líder de Arquitectura (Clean Architecture), QA Lead (cobertura Pytest >= 80% y DoD), Desarrolladores (PEP 8 y TDD) e Ingeniero DevOps (configuración segura .env y rollback).", bullet_style))
    story.append(Paragraph("• <b>Canales y Telemetría:</b> Standups diarios de 15 minutos, bitácora inmutable de defectos y registro estructurado de eventos en 'logs/farmacia_vannesa.log' con rotación automática (RotatingFileHandler de 5 MB) y formato ISO 8601.", bullet_style))
    story.append(Paragraph("• <b>Definition of Done (DoD):</b> Todo cambio debe tener 100% de tests unitarios aprobados, cobertura >= 80% y validación de linters PEP 8 sin advertencias bloqueantes.", bullet_style))

    # ----------------------------------------------------
    # 2. OBJETIVOS
    # ----------------------------------------------------
    story.append(Paragraph("2. Objetivos de la Auditoría de Calidad", h1_style))
    story.append(Paragraph("<b>Objetivo General:</b> Evaluar de forma objetiva, sistemática y rigurosa la efectividad, seguridad, calidad y alineación de los controles de TI en el Sistema Web de Farmacia Vannesa, garantizando confidencialidad, integridad y disponibilidad, así como el cumplimiento de los estándares de calidad en las 5 fases del SDLC.", body_style))
    story.append(Paragraph("<b>Objetivos Específicos:</b> Validar requerimientos atómicos y checklist IEEE 830; auditar modelo de datos relacional con los 11 campos mandatorios y Clean Architecture; verificar cumplimiento PEP 8 y seguridad estática OWASP; comprobar cobertura Pytest >= 80% y pruebas de valores límite; y auditar endpoint de monitoreo /health y plan de rollback < 15 min.", body_style))

    # ----------------------------------------------------
    # 3. ALCANCE Y MARCOS
    # ----------------------------------------------------
    story.append(Paragraph("3. Alcance, Exclusiones y Marcos de Referencia", h1_style))
    story.append(Paragraph("<b>Alcance:</b> Cubre el 100% del ciclo de vida del software: requerimientos SRS, modelo de datos relacional, código fuente Flask/Python, pruebas Pytest, scripts de respaldo/rollback y configuración de despliegue.<br/><b>Exclusiones:</b> Servidores físicos on-premise, racks, UPS físicos de centros de cómputo, cableado estructurado y redes Wi-Fi de visitas.", body_style))
    
    c_table_data = [
        [Paragraph("Estándar / Marco", th_style), Paragraph("Ámbito de Aplicación", th_style), Paragraph("Criterios Clave Evaluados", th_style)],
        [Paragraph("ISO 19011:2018", td_bold_style), Paragraph("Metodología de Auditoría", td_style), Paragraph("Principios de auditoría, enfoque basado en riesgos, evidencia objetiva y formalidad.", td_style)],
        [Paragraph("ISO/IEC 25010:2011", td_bold_style), Paragraph("Modelo de Calidad Software", td_style), Paragraph("Adecuación funcional, fiabilidad, mantenibilidad, modularidad y seguridad.", td_style)],
        [Paragraph("IEEE 830 / ISO 29148", td_bold_style), Paragraph("Ingeniería de Requerimientos", td_style), Paragraph("Checklist de 8 características: Correcto, No ambiguo, Completo, Consistente, Verificable, etc.", td_style)],
        [Paragraph("CMMI-DEV v2.0", td_bold_style), Paragraph("Madurez de Procesos SDLC", td_style), Paragraph("Áreas: Planificación, Calidad de Proceso y Producto (PPQA), Verificación y Validación.", td_style)],
        [Paragraph("OWASP Top 10 & PEP 8", td_bold_style), Paragraph("Construcción y Seguridad", td_style), Paragraph("Mitigación de Inyección SQL, XSS, contraseñas seguras y guía de estilo Python.", td_style)]
    ]
    t_criterios = Table(c_table_data, colWidths=[1.6 * inch, 1.8 * inch, 3.6 * inch])
    t_criterios.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_alt_row, colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_criterios)
    story.append(Spacer(1, 8))

    # ----------------------------------------------------
    # 4. MATRIZ DE RIESGOS (1 A 3)
    # ----------------------------------------------------
    story.append(Paragraph("4. Matriz de Evaluación de Riesgos de Calidad (Metodología 1 a 3)", h1_style))
    story.append(Paragraph("La escala evalúa Probabilidad (1 a 3) e Impacto (1 a 3): Nivel de Severidad = P × I (1-2 Bajo, 3-4 Medio, 6-9 Alto/Crítico).", body_style))

    risk_table_data = [
        [Paragraph("ID", th_style), Paragraph("Descripción del Riesgo de Calidad", th_style), Paragraph("P", th_style), Paragraph("I", th_style), Paragraph("R. Inh.", th_style), Paragraph("Controles Existentes", th_style), Paragraph("R. Res.", th_style), Paragraph("Estrategia / Plan de Acción", th_style)],
        [Paragraph("R-CAL-01", td_bold_style), Paragraph("Ambigüedad en requerimientos causa fallas en stock e inventario.", td_style), Paragraph("3", td_style), Paragraph("3", td_style), Paragraph("<b>9 (Alto)</b>", td_style), Paragraph("Revisiones informales.", td_style), Paragraph("2x2=4", td_style), Paragraph("Mitigar: Checklist IEEE 830 y atómicos.", td_style)],
        [Paragraph("R-CAL-02", td_bold_style), Paragraph("Acoplamiento en Flask impide tests y escalabilidad.", td_style), Paragraph("3", td_style), Paragraph("2", td_style), Paragraph("<b>6 (Alto)</b>", td_style), Paragraph("Uso parcial de módulos.", td_style), Paragraph("2x1=2", td_style), Paragraph("Mitigar: Clean Architecture estricta.", td_style)],
        [Paragraph("R-CAL-03", td_bold_style), Paragraph("Deuda técnica y no apego a PEP 8 eleva fallos y costos.", td_style), Paragraph("2", td_style), Paragraph("2", td_style), Paragraph("4 (Med)", td_style), Paragraph("Revisión visual ocasional.", td_style), Paragraph("1x2=2", td_style), Paragraph("Mitigar: Linters Flake8 y escaneo SAST.", td_style)],
        [Paragraph("R-CAL-04", td_bold_style), Paragraph("Baja cobertura de tests en ventas causa sobreventas.", td_style), Paragraph("3", td_style), Paragraph("3", td_style), Paragraph("<b>9 (Alto)</b>", td_style), Paragraph("Testing manual básico.", td_style), Paragraph("1x2=2", td_style), Paragraph("Mitigar: Pytest >= 80% y valores límite.", td_style)],
        [Paragraph("R-CAL-05", td_bold_style), Paragraph("Despliegues manuales y fallas en migraciones de BD.", td_style), Paragraph("2", td_style), Paragraph("3", td_style), Paragraph("<b>6 (Alto)</b>", td_style), Paragraph("Respaldo manual ocasional.", td_style), Paragraph("1x2=2", td_style), Paragraph("Mitigar: backup_db.py (Rollback < 15 min).", td_style)],
    ]
    t_risk = Table(risk_table_data, colWidths=[0.6 * inch, 2.0 * inch, 0.25 * inch, 0.25 * inch, 0.65 * inch, 1.15 * inch, 0.55 * inch, 1.55 * inch])
    t_risk.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_alt_row, colors.white]),
        ('ALIGN', (2, 1), (4, -1), 'CENTER'),
        ('ALIGN', (6, 1), (6, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_risk)
    story.append(Spacer(1, 8))

    # ----------------------------------------------------
    # 5. PROGRAMA DE TRABAJO (25 AUDITORÍAS EN 2 PASOS)
    # ----------------------------------------------------
    story.append(Paragraph("5. Programa de Trabajo Detallado (25 Auditorías en 2 Pasos)", h1_style))
    story.append(Paragraph("A continuación se especifican las 25 auditorías técnicas del SDLC con procedimiento en dos pasos operativos:", body_style))

    def make_audit_table(code, name, obj, step1, step2, criteria, evid):
        data = [
            [Paragraph(f"<b>Auditoría {code}: {name}</b>", td_bold_style), Paragraph("", td_style)],
            [Paragraph("<b>Objetivo:</b>", td_bold_style), Paragraph(obj, td_style)],
            [Paragraph("<b>Paso 1 (Ejecución):</b>", td_bold_style), Paragraph(step1, td_style)],
            [Paragraph("<b>Paso 2 (Verificación):</b>", td_bold_style), Paragraph(step2, td_style)],
            [Paragraph("<b>Criterio Aceptación:</b>", td_bold_style), Paragraph(criteria, td_style)],
            [Paragraph("<b>Evidencia / Papel:</b>", td_bold_style), Paragraph(evid, td_style)],
        ]
        t = Table(data, colWidths=[1.7 * inch, 5.3 * inch])
        t.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)),
            ('BACKGROUND', (0, 0), (1, 0), c_bg_light),
            ('GRID', (0, 0), (-1, -1), 0.5, c_border),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        return t

    # MÓDULO 1
    story.append(Paragraph("Módulo 1: Fase de Análisis de Requerimientos (5 Auditorías)", h2_style))
    story.append(make_audit_table(
        "A-01", "Revisión de Atomicidad de Requerimientos",
        "Verificar que cada requerimiento funcional describa una única funcionalidad.",
        "Seleccionar al azar 5 requerimientos de la especificación SRS. Analizar que no mezclen responsabilidades operativas disjuntas.",
        "Documentar la matriz de atomicidad con la justificación individual y propuesta de descomposición.",
        "100% de los requerimientos auditados debe describir una única necesidad funcional comprobable.",
        "Matriz de evaluación de atomicidad | Estándar: ISO/IEC/IEEE 29148:2018 (Cláusula 5.2.5)"
    ))
    story.append(Spacer(1, 3))

    # Muestreo atómico en tabla
    rf_sample_data = [
        [Paragraph("Requerimiento Muestreado", th_style), Paragraph("Descripción Original", th_style), Paragraph("Evaluación de Atomicidad", th_style), Paragraph("Dictamen y Ajuste Requerido", th_style)],
        [Paragraph("RF01: Autenticación y Perfiles", td_bold_style), Paragraph("Inicio de sesión seguro con contraseña encriptada, asignando roles (Admin, Farmacéutico, Vendedor) y restringiendo accesos.", td_style), Paragraph("Parcialmente Atómico. Agrupa autenticación, almacenamiento seguro (hashing) y autorización RBAC en un solo texto.", td_style), Paragraph("Dividir en: RF01.1 (Autenticación), RF01.2 (Hashing seguro bcrypt), RF01.3 (Control RBAC).", td_style)],
        [Paragraph("RF03: Catalogación con 11 Campos", td_bold_style), Paragraph("Registrar medicamentos con código de barra, principio activo, concentración, laboratorio, lote, vencimiento, costo, precio, stock.", td_style), Paragraph("No Atómico. Mezcla el catálogo maestro del producto con la gestión de existencias físicas por lote.", td_style), Paragraph("Desacoplar en: RF03.1 (Catálogo maestro 11 campos) y RF03.2 (Existencias por lote/vencimiento).", td_style)],
        [Paragraph("RF06: Módulo de Ventas y Bloqueo", td_bold_style), Paragraph("Procesar ventas en carrito, calcular subtotales e impuestos, y bloquear ventas si exceden el stock físico.", td_style), Paragraph("No Atómico. Une cálculo comercial de venta con la regla crítica de bloqueo y reserva concurrente de stock.", td_style), Paragraph("Separar en: RF06.1 (Cálculo y ticket de venta) y RF06.2 (Validación concurrente atómica de stock).", td_style)],
        [Paragraph("RF09: Inventario y Kardex", td_bold_style), Paragraph("Actualizar inventario en tiempo real con entradas por compras, salidas por ventas, mermas y ajustes manuales.", td_style), Paragraph("Parcialmente Atómico. Agrupa movimientos automáticos con ajustes manuales que requieren permisos distintos.", td_style), Paragraph("Dividir en: RF09.1 (Kardex transaccional automático) y RF09.2 (Ajustes manuales y mermas por Admin).", td_style)],
        [Paragraph("RF12: Alertas de Stock Crítico", td_bold_style), Paragraph("Emitir alertas en panel si un fármaco tiene menos de 10 unidades o vence en 30 días.", td_style), Paragraph("No Atómico y Rígido. Une stock mínimo con proximidad de vencimiento y usa umbrales 'quemados'.", td_style), Paragraph("Ajustar a umbrales dinámicos: RF12.1 (Alerta stock < stock_minimo) y RF12.2 (Alerta por caducidad).", td_style)]
    ]
    t_rf = Table(rf_sample_data, colWidths=[1.5 * inch, 2.1 * inch, 1.8 * inch, 1.6 * inch])
    t_rf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_alt_row, colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_rf)
    story.append(Spacer(1, 3))

    story.append(make_audit_table("A-02", "Revisión de Claridad y Definición", "Verificar que los requerimientos carezcan de ambigüedades.", "Inspeccionar términos vagos ('rápido', 'adecuado'). Confirmar redacción técnica adecuada.", "Elaborar informe técnico con observaciones semánticas y recomendaciones.", "100% de los requerimientos debe carecer de ambigüedades.", "Matriz de claridad léxica | Estándar: IEEE 830 (No Ambigüedad)"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-03", "Revisión de Verificabilidad", "Verificar que cada requerimiento pueda validarse mediante un caso de prueba.", "Evaluar la testabilidad de cada requerimiento funcional frente a aserciones en Pytest.", "Generar ficha técnica vinculando el requerimiento con su correspondiente test automatizado.", "100% de los requerimientos debe ser verificable mediante pruebas computables.", "Ficha técnica de verificabilidad | Estándar: IEEE 830"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-04", "Revisión de Trazabilidad Bidireccional", "Verificar la correspondencia bidireccional entre requerimientos, código y tests.", "Revisar matriz RTM completa. Verificar que cada requerimiento tenga caso de uso, repositorio y test.", "Documentar matriz RTM consolidada y porcentaje de cobertura de trazabilidad.", "0% de requerimientos huérfanos y cobertura de trazabilidad >= 95%.", "Matriz RTM bidireccional | Estándar: CMMI-DEV v2.0 (REQM)"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-05", "Cumplimiento de Normas IEEE 830", "Evaluar la especificación frente a las 8 características mandatorias de calidad.", "Aplicar checklist formal: Correcto, No ambiguo, Completo, Consistente, Clasificado, Verificable, Modificable, Trazable.", "Emitir lista de chequeo formal firmada con el porcentaje de conformidad obtenido.", "Cumplimiento >= 90% en las 8 características del estándar IEEE 830.", "Checklist formal IEEE 830 | Estándar: IEEE 830:1998"))
    story.append(Spacer(1, 6))

    # MÓDULO 2
    story.append(Paragraph("Módulo 2: Fase de Diseño de Software (5 Auditorías)", h2_style))
    story.append(make_audit_table("A-06", "Revisión del Modelo de Datos (11 Campos y 3FN)", "Verificar que el modelo de productos contemple los 11 campos mandatorios y normalización 3FN.", "Inspeccionar DDL de tabla products: name, generic_name, product_code, description, stock, presentation, laboratory, expiration_date, dose, cost_price y sale_price.", "Verificar índice UNIQUE idx_products_code, triggers de cantidad positiva y Foreign Keys.", "100% de los 11 campos presentes con tipos adecuados (DECIMAL, DATE, INT).", "Script DDL auditado y diccionario de datos | Estándar: Normalización 3FN"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-07", "Revisión de la Arquitectura de Seguridad", "Verificar que la autenticación aplique funciones de hashing robustas y protección de rutas.", "Revisar auth_service.py y verificar hash + salt con Werkzeug (scrypt/pbkdf2). Confirmar middleware de rutas.", "Capturar la estructura de almacenamiento seguro de contraseñas y decoradores.", "100% de contraseñas con hash robusto y 0 rutas administrativas expuestas.", "Captura hash BD y código de decoradores | Estándar: OWASP ASVS"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-08", "Revisión del Diseño de Integración Dual", "Verificar que la integración dual (Supabase Cloud y SQLite local) opere con transacciones atómicas.", "Examinar inyección de dependencias en main.py y conmutación transparente ante caída de red.", "Documentar flujo de conmutación resiliente y consistencia transaccional ACID.", "Persistencia transparente con soporte de transacciones ACID en ambos motores.", "Diagrama de integración y prueba de conmutación | Estándar: Resiliencia BCP"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-09", "Revisión del Diseño de Interfaz de Usuario (UI/UX)", "Evaluar ergonomía y velocidad operativa de despacho en mostrador farmacéutico (POS).", "Inspeccionar sales.html e inventory.html. Medir clics para buscar por código de barra y totalizar venta.", "Verificar alertas visuales destacadas para productos con bajo stock (< 10) y próximos a vencer.", "Operación de venta ágil en mostrador con alertas visibles de stock crítico.", "Evaluación heurística de usabilidad POS | Estándar: ISO 9241-11"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-10", "Revisión del Diseño de Escalabilidad y Concurrencia", "Verificar que el diseño soporte al menos 50 usuarios concurrentes sin quiebres de inventario.", "Analizar uso de índices DDL ('idx_products_code') y validación atómica previa al descuento de stock.", "Documentar análisis de contención y aislamiento transaccional para operaciones concurrentes.", "Soporte para >= 50 usuarios concurrentes sin condiciones de carrera.", "Reporte de diseño de escalabilidad | Estándar: ISO/IEC 25010"))
    story.append(Spacer(1, 6))

    # MÓDULO 3
    story.append(Paragraph("Módulo 3: Fase de Construcción de Software (5 Auditorías)", h2_style))
    story.append(make_audit_table("A-11", "Revisión de Calidad del Código y Complejidad", "Verificar código libre de vulnerabilidades críticas y complejidad ciclomática controlada.", "Ejecutar Flake8 y Radon sobre todo el código en 'app/'. Identificar code smells y funciones complejas.", "Documentar matriz de complejidad asegurando que ninguna función exceda un valor de 10.", "Complejidad ciclomática < 10 en todas las funciones y 0 defectos críticos.", "Reporte Flake8 y reporte de complejidad Radon | Estándar: McCabe"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-12", "Revisión de Cobertura de Pruebas Unitarias", "Verificar que la cobertura de pruebas automatizadas en la lógica de negocio sea >= 80%.", "Ejecutar suite con 'pytest --cov=app/application/services --cov=app/domain'. Medir líneas cubiertas.", "Generar reporte Coverage.py demostrando el cumplimiento del umbral del Definition of Done.", "Cobertura >= 80% (Verificado en proyecto: 84% de cobertura alcanzada).", "Reporte Coverage.py con 84% alcanzado | Estándar: IEEE 1008-1987"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-13", "Revisión de Codificación Segura (OWASP Top 10)", "Verificar mitigación de inyección SQL, XSS, CSRF y exposición de datos.", "Ejecutar escaneo estático SAST con Bandit. Comprobar queries parametrizadas y tokens CSRF.", "Emitir reporte ejecutivo de hallazgos SAST categorizados por nivel de severidad.", "0 vulnerabilidades de inyección SQL y 0 vulnerabilidades de severidad alta.", "Reporte SAST generado con Bandit | Estándar: OWASP Top 10"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-14", "Revisión de Gestión de Dependencias y CVEs", "Verificar que las librerías en requirements.txt estén fijadas y libres de vulnerabilidades conocidas.", "Inspeccionar dependencias y ejecutar 'pip-audit' contrastando paquetes contra la base de datos NVD.", "Documentar la lista de dependencias y registrar la ausencia de CVEs críticos.", "100% de dependencias fijadas y 0 vulnerabilidades críticas no mitigadas.", "Reporte de escaneo de dependencias pip-audit | Estándar: ISO/IEC 25010"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-15", "Revisión de Estándares de Codificación PEP 8", "Verificar cumplimiento de la guía de estilo oficial de Python (PEP 8) y docstrings.", "Ejecutar Flake8 sobre módulos de la aplicación. Comprobar sangrías, naming conventions y docstrings.", "Elaborar informe de densidad de defectos de estilo y verificación de legibilidad.", "Cumplimiento >= 90% de reglas de estilo PEP 8.", "Reporte de linter Flake8 | Estándar: PEP 8"))
    story.append(Spacer(1, 6))

    # MÓDULO 4
    story.append(Paragraph("Módulo 4: Fase de Despliegue y Puesta en Producción (5 Auditorías)", h2_style))
    story.append(make_audit_table("A-16", "Revisión del Proceso de Entrega y Empaquetado", "Verificar empaquetado reproducible y control de versiones formal.", "Inspeccionar 'wsgi.py', 'Procfile', 'vannesa.spec'. Comprobar consistencia para servidores WSGI.", "Documentar bitácora de empaquetado y prueba de ejecución limpia en entorno independiente.", "Proceso de despliegue 100% documentado, versionado y reproducible.", "Guía operativa de despliegue y Procfile | Estándar: CMMI-DEV v2.0"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-17", "Revisión del Plan de Rollback y Respaldo", "Verificar que el plan de rollback pueda ejecutarse en menos de 15 minutos (RTO < 15 min).", "Ejecutar 'backup_db.py --backup' para validar respaldo con verificación de integridad. Probar 'backup_db.py --restore'.", "Registrar tiempo cronometrado de restauración y consistencia física de los datos restaurados.", "Tiempo de recuperación (RTO) < 15 minutos (Verificado: < 10 segundos con backup_db.py).", "Log de backup_db.py y verificación de integridad | Estándar: ISO 22301"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-18", "Revisión de Aislamiento de Entornos de Prueba", "Verificar que las pruebas unitarias operen en bases de datos temporales sin alterar producción.", "Inspeccionar 'tests/conftest.py'. Comprobar que los tests generen bases temporales independientes.", "Documentar la prueba de aislamiento confirmando que los tests no alteran 'vannesa_db.sqlite'.", "100% de aislamiento entre datos de pruebas y datos de producción.", "Evidencia de fixtures aisladas en tests/conftest.py | Estándar: ISO/IEC 25010"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-19", "Revisión de Variables de Entorno y Secretos (.env)", "Verificar que el 100% de los secretos y claves residan en variables de entorno seguras (.env).", "Escanear código en busca de credenciales hardcodeadas. Comprobar plantilla .env.example y .gitignore.", "Generar reporte de auditoría de exclusión de secretos en el control de versiones Git.", "100% de secretos en variables de entorno y 0 credenciales expuestas en Git.", "Archivo .env.example y reporte de escaneo | Estándar: Twelve-Factor App"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-20", "Revisión de Monitoreo y Logging Estructurado", "Verificar registro de eventos con marcas de tiempo ISO 8601 y rotación de bitácoras.", "Inspeccionar RotatingFileHandler en 'main.py' y generación de 'logs/farmacia_vannesa.log' (5 MB).", "Capturar extracto de logs operativos con solicitudes reales, códigos HTTP y latencia.", "Registro estructurado de eventos con IP, tiempo de respuesta y rotación activa.", "Archivo 'logs/farmacia_vannesa.log' | Estándar: OWASP ASVS"))
    story.append(Spacer(1, 6))

    # MÓDULO 5
    story.append(Paragraph("Módulo 5: Fase de Test y Aseguramiento de Calidad (5 Auditorías)", h2_style))
    story.append(make_audit_table("A-21", "Revisión de Cobertura de Requerimientos Funcionales", "Verificar que los requerimientos funcionales críticos cuenten con pruebas automatizadas.", "Cruzar la matriz de trazabilidad frente a los 20 tests implementados en 'tests/'.", "Documentar índice de cobertura de requerimientos demostrando cumplimiento >= 90%.", "Cobertura de requerimientos funcionales críticos >= 90%.", "Matriz de cobertura requerimiento-prueba | Estándar: ISO/IEC/IEEE 29119-2"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-22", "Revisión de Pruebas Críticas y Transaccionales", "Verificar que el 100% de las pruebas transaccionales críticas se aprueben satisfactoriamente.", "Ejecutar tests transaccionales: descuento atómico de inventario, kardex y actualización de balance de caja.", "Documentar reporte de ejecución de pruebas críticas con resultado 100% PASS.", "100% de pruebas críticas aprobadas y 0 defectos bloqueantes.", "Reporte de ejecución de pruebas críticas (100% PASS) | Estándar: ISO/IEC/IEEE 29119-2"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-23", "Revisión de Evidencia Técnica Verificable", "Verificar que el 100% de las pruebas del plan cuente con evidencia técnica objetiva.", "Inspeccionar carpetas de evidencias, archivos JSON de /health, logs de Pytest y DDL.", "Consolidar dossier de evidencias digitales archivadas con firma del auditor responsable.", "100% de las pruebas sustentadas con evidencias técnicas trazables.", "Dossier de evidencias digitales verificables | Estándar: ISO 19011:2018"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-24", "Revisión de Pruebas de Regresión y Valores Límite", "Verificar suite de regresión automatizada que evalúe casos de frontera (Boundary Testing).", "Ejecutar 'test_quality_and_services.py': venta de última unidad (stock 0), sobreventa (+1), cantidades negativas.", "Registrar resultados de aserciones de valores frontera y resistencia ante entradas anómalas.", "Suite de regresión automatizada ejecutable en < 10s con 100% PASS.", "Suite de pruebas de regresión y valores límite | Estándar: ISO/IEC/IEEE 29119-4"))
    story.append(Spacer(1, 3))
    story.append(make_audit_table("A-25", "Revisión de Rendimiento y Health Check", "Verificar que los endpoints respondan con latencia menor a 2.0 segundos.", "Solicitar endpoint '/health' y medir latencia. Comprobar código HTTP 200 OK y JSON con estado 'UP'.", "Documentar métricas de latencia registradas en las bitácoras estructuradas.", "Tiempo de respuesta < 2.0 segundos (Verificado en proyecto: 1.1 ms en /health).", "Registro de latencia de /health en logs estructurados | Estándar: ISO/IEC 25010"))
    story.append(Spacer(1, 8))

    # ----------------------------------------------------
    # 6. TABLA FINAL CONSOLIDADA (25 AUDITORÍAS)
    # ----------------------------------------------------
    story.append(Paragraph("6. Tabla Resumen del Programa de Trabajo (25 Auditorías)", h1_style))
    story.append(Paragraph("A continuación se consolida la matriz operativa completa cruzando código de riesgo, fase del SDLC, auditoría, pasos, evidencia y responsable asignado:", body_style))

    summary_rows_pdf = [
        [Paragraph("Cód.", th_style), Paragraph("Fase SDLC", th_style), Paragraph("Auditoría", th_style), Paragraph("Procedimiento Operativo", th_style), Paragraph("Evidencia Principal", th_style), Paragraph("Formato", th_style), Paragraph("Responsable", th_style)],
        [Paragraph("R-CAL-01", td_bold_style), Paragraph("1. Requerimientos", td_style), Paragraph("A-01: Atomicidad", td_style), Paragraph("Paso 1: Muestreo 5 RFs / Paso 2: Matriz atómica.", td_style), Paragraph("Matriz evaluación atómica", td_style), Paragraph("Word/PDF", td_style), Paragraph("Auditor Req.", td_style)],
        [Paragraph("R-CAL-01", td_bold_style), Paragraph("1. Requerimientos", td_style), Paragraph("A-02: Claridad", td_style), Paragraph("Paso 1: Análisis léxico / Paso 2: Sin ambigüedad.", td_style), Paragraph("Matriz claridad léxica", td_style), Paragraph("Word/PDF", td_style), Paragraph("Auditor Req.", td_style)],
        [Paragraph("R-CAL-01", td_bold_style), Paragraph("1. Requerimientos", td_style), Paragraph("A-03: Verificabilidad", td_style), Paragraph("Paso 1: Testabilidad / Paso 2: Ficha aserciones.", td_style), Paragraph("Ficha verificabilidad", td_style), Paragraph("Excel", td_style), Paragraph("Auditor QA", td_style)],
        [Paragraph("R-CAL-01", td_bold_style), Paragraph("1. Requerimientos", td_style), Paragraph("A-04: Trazabilidad", td_style), Paragraph("Paso 1: Matriz RTM / Paso 2: Detección huérfanos.", td_style), Paragraph("Matriz RTM bidireccional", td_style), Paragraph("Excel", td_style), Paragraph("Auditor QA", td_style)],
        [Paragraph("R-CAL-01", td_bold_style), Paragraph("1. Requerimientos", td_style), Paragraph("A-05: Norma IEEE 830", td_style), Paragraph("Paso 1: Checklist 8 criterios / Paso 2: Acta.", td_style), Paragraph("Checklist IEEE 830", td_style), Paragraph("PDF", td_style), Paragraph("Auditor QA", td_style)],
        [Paragraph("R-CAL-02", td_bold_style), Paragraph("2. Diseño", td_style), Paragraph("A-06: Modelo de Datos", td_style), Paragraph("Paso 1: DDL 11 campos / Paso 2: 3FN e índices.", td_style), Paragraph("Script DDL y diccionario", td_style), Paragraph("SQL/PDF", td_style), Paragraph("Auditor Calidad", td_style)],
        [Paragraph("R-CAL-03", td_bold_style), Paragraph("2. Diseño", td_style), Paragraph("A-07: Arq. Seguridad", td_style), Paragraph("Paso 1: Hash scrypt / Paso 2: Middleware rutas.", td_style), Paragraph("Captura hash BD y código", td_style), Paragraph("Código/PDF", td_style), Paragraph("Auditor Seg.", td_style)],
        [Paragraph("R-CAL-02", td_bold_style), Paragraph("2. Diseño", td_style), Paragraph("A-08: Integración Dual", td_style), Paragraph("Paso 1: Inyección / Paso 2: Conmutación resiliente.", td_style), Paragraph("Diagrama arquitectura", td_style), Paragraph("UML/PDF", td_style), Paragraph("Auditor Calidad", td_style)],
        [Paragraph("R-CAL-01", td_bold_style), Paragraph("2. Diseño", td_style), Paragraph("A-09: Diseño UI/UX", td_style), Paragraph("Paso 1: Ergonomía POS / Paso 2: Alertas stock.", td_style), Paragraph("Evaluación heurística UI", td_style), Paragraph("PDF/Figma", td_style), Paragraph("Auditor Calidad", td_style)],
        [Paragraph("R-CAL-02", td_bold_style), Paragraph("2. Diseño", td_style), Paragraph("A-10: Escalabilidad", td_style), Paragraph("Paso 1: Concurrencia >= 50 / Paso 2: Índices BD.", td_style), Paragraph("Reporte escalabilidad", td_style), Paragraph("PDF", td_style), Paragraph("Auditor Infra.", td_style)],
        [Paragraph("R-CAL-03", td_bold_style), Paragraph("3. Construcción", td_style), Paragraph("A-11: Calidad Código", td_style), Paragraph("Paso 1: Estático Flake8 / Paso 2: Radon < 10.", td_style), Paragraph("Reporte Flake8 y Radon", td_style), Paragraph("HTML/PDF", td_style), Paragraph("Auditor Calidad", td_style)],
        [Paragraph("R-CAL-04", td_bold_style), Paragraph("3. Construcción", td_style), Paragraph("A-12: Tests Unitarios", td_style), Paragraph("Paso 1: Pytest / Paso 2: Coverage >= 80% (84%).", td_style), Paragraph("Reporte Coverage 84%", td_style), Paragraph("HTML/PDF", td_style), Paragraph("Auditor QA", td_style)],
        [Paragraph("R-CAL-03", td_bold_style), Paragraph("3. Construcción", td_style), Paragraph("A-13: OWASP Top 10", td_style), Paragraph("Paso 1: Bandit SAST / Paso 2: Queries seguras.", td_style), Paragraph("Reporte escáner Bandit", td_style), Paragraph("JSON/PDF", td_style), Paragraph("Auditor Seg.", td_style)],
        [Paragraph("R-CAL-03", td_bold_style), Paragraph("3. Construcción", td_style), Paragraph("A-14: Dependencias", td_style), Paragraph("Paso 1: pip-audit CVE / Paso 2: Fijación versions.", td_style), Paragraph("Reporte de escaneo CVE", td_style), Paragraph("JSON/TXT", td_style), Paragraph("Auditor Seg.", td_style)],
        [Paragraph("R-CAL-03", td_bold_style), Paragraph("3. Construcción", td_style), Paragraph("A-15: Estándar PEP 8", td_style), Paragraph("Paso 1: Linter Flake8 / Paso 2: Docstrings.", td_style), Paragraph("Reporte de estilo PEP 8", td_style), Paragraph("TXT/PDF", td_style), Paragraph("Auditor Calidad", td_style)],
        [Paragraph("R-CAL-05", td_bold_style), Paragraph("4. Despliegue", td_style), Paragraph("A-16: Proceso Entrega", td_style), Paragraph("Paso 1: Empaquetado / Paso 2: Procfile y wsgi.", td_style), Paragraph("Guía de despliegue", td_style), Paragraph("PDF", td_style), Paragraph("DevOps", td_style)],
        [Paragraph("R-CAL-05", td_bold_style), Paragraph("4. Despliegue", td_style), Paragraph("A-17: Plan Rollback", td_style), Paragraph("Paso 1: Respaldo / Paso 2: Simulacro backup_db.", td_style), Paragraph("Log backup_db (< 10s)", td_style), Paragraph("Log/PDF", td_style), Paragraph("DevOps", td_style)],
        [Paragraph("R-CAL-05", td_bold_style), Paragraph("4. Despliegue", td_style), Paragraph("A-18: Aislamiento", td_style), Paragraph("Paso 1: Fixtures temp / Paso 2: Cero prod touch.", td_style), Paragraph("Evidencia conftest.py", td_style), Paragraph("Código", td_style), Paragraph("DevOps", td_style)],
        [Paragraph("R-CAL-03", td_bold_style), Paragraph("4. Despliegue", td_style), Paragraph("A-19: Secretos (.env)", td_style), Paragraph("Paso 1: Escaneo secretos / Paso 2: .env.example.", td_style), Paragraph("Plantilla .env.example", td_style), Paragraph("Archivo", td_style), Paragraph("Auditor Seg.", td_style)],
        [Paragraph("R-CAL-05", td_bold_style), Paragraph("4. Despliegue", td_style), Paragraph("A-20: Monitoreo/Logs", td_style), Paragraph("Paso 1: RotatingHandler / Paso 2: farmacia.log.", td_style), Paragraph("Logs farmacia_vannesa.log", td_style), Paragraph("Log", td_style), Paragraph("DevOps", td_style)],
        [Paragraph("R-CAL-04", td_bold_style), Paragraph("5. Test", td_style), Paragraph("A-21: Cobertura Req.", td_style), Paragraph("Paso 1: Cruce RF vs Pytest / Paso 2: Aserciones.", td_style), Paragraph("Matriz trazabilidad", td_style), Paragraph("Excel", td_style), Paragraph("Ingeniero QA", td_style)],
        [Paragraph("R-CAL-04", td_bold_style), Paragraph("5. Test", td_style), Paragraph("A-22: Pruebas Críticas", td_style), Paragraph("Paso 1: Transacciones / Paso 2: 100% PASS.", td_style), Paragraph("Reporte pruebas transacc.", td_style), Paragraph("HTML", td_style), Paragraph("Ingeniero QA", td_style)],
        [Paragraph("R-CAL-04", td_bold_style), Paragraph("5. Test", td_style), Paragraph("A-23: Evidencia Técnica", td_style), Paragraph("Paso 1: Recopilación / Paso 2: Dossier verificado.", td_style), Paragraph("Carpeta evidencias", td_style), Paragraph("ZIP/PDF", td_style), Paragraph("Ingeniero QA", td_style)],
        [Paragraph("R-CAL-04", td_bold_style), Paragraph("5. Test", td_style), Paragraph("A-24: Regresión/Límites", td_style), Paragraph("Paso 1: Boundary testing / Paso 2: Stock cero.", td_style), Paragraph("Suite quality_and_services", td_style), Paragraph("Código", td_style), Paragraph("Ingeniero QA", td_style)],
        [Paragraph("R-CAL-05", td_bold_style), Paragraph("5. Test", td_style), Paragraph("A-25: Rendimiento", td_style), Paragraph("Paso 1: GET /health / Paso 2: Latencia < 2.0s (1.1ms).", td_style), Paragraph("Logs de latencia /health", td_style), Paragraph("JSON/Log", td_style), Paragraph("Ingeniero QA", td_style)]
    ]
    t_sum_pdf = Table(summary_rows_pdf, colWidths=[0.55 * inch, 1.05 * inch, 1.15 * inch, 1.75 * inch, 1.25 * inch, 0.55 * inch, 0.70 * inch])
    t_sum_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_alt_row, colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
    ]))
    story.append(t_sum_pdf)
    story.append(Spacer(1, 8))

    # ----------------------------------------------------
    # 7. FORMALIZACIÓN
    # ----------------------------------------------------
    story.append(Paragraph("7. Calificación de Hallazgos y Formalización Institucional", h1_style))
    story.append(Paragraph("• <b>No Conformidad Mayor (NC Mayor):</b> Incumplimiento crítico de integridad de stock, criptografía o caída del servicio. Requiere subsanación obligatoria previa a producción.", bullet_style))
    story.append(Paragraph("• <b>No Conformidad Menor (NC Menor):</b> Desviación que no compromete la operación crítica (estilo PEP 8 o cobertura levemente bajo umbral).", bullet_style))
    story.append(Paragraph("• <b>Oportunidad de Mejora (OM):</b> Recomendación proactiva para optimizar modularidad o rendimiento.", bullet_style))
    story.append(Spacer(1, 6))

    sig_data = [
        [Paragraph("<b>Por el Equipo Auditor Especialista:</b><br/><br/><br/>_____________________________________<br/><b>Auditor Líder de Calidad de Software</b><br/>Certificación CISA / ISO 19011 Lead Auditor", td_style),
         Paragraph("<b>Por la Dirección de Farmacia Vannesa:</b><br/><br/><br/>_____________________________________<br/><b>Gerencia General / Patrocinador del Proyecto</b><br/>Farmacia Vannesa — Dirección Ejecutiva", td_style)],
        [Paragraph("<i>Fecha: Octubre 2026 | Estado: Aprobado</i>", td_style),
         Paragraph("<i>Fecha: Octubre 2026 | Estado: Aprobado</i>", td_style)]
    ]
    t_sig = Table(sig_data, colWidths=[3.5 * inch, 3.5 * inch])
    t_sig.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_sig)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Documento PDF guardado exitosamente en: {pdf_filename}")

if __name__ == "__main__":
    build_pdf()
