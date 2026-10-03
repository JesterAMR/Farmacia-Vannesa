# -*- coding: utf-8 -*-
"""
Script generador de los documentos oficiales en Word (.docx) y PDF (.pdf):
'Plan y Pruebas de Auditoría de Calidad — Evaluación Rigurosa de Parámetros'
Farmacia Vannesa — Sistema de Gestión Farmacéutica e Inventarios
Explicita de forma transparente y objetiva las pruebas que resultaron EXITOSAS
y aquellas que NO CUMPLIERON con los parámetros respectivos exigidos.
"""

import os
import sys
import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from docx_helpers import set_cell_background, set_cell_margins, set_table_borders, add_callout

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# 1. GENERACIÓN DEL DOCUMENTO WORD (.DOCX)
# ==============================================================================
def generate_docx():
    docx_path = os.path.join(BASE_DIR, "Plan_y_Pruebas_Auditoria_Calidad_Farmacia_Vannesa.docx")
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("FARMACIA VANNESA | PLAN Y PRUEBAS DE AUDITORÍA DE CALIDAD (SDLC)")
        hrun.font.name = 'Calibri'
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(0x7F, 0x8C, 0x8D)

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        frun1 = fp.add_run("Evaluación Rigurosa de Parámetros de Calidad | Resultados Exitosos y No Exitosos")
        frun1.font.name = 'Calibri'
        frun1.font.size = Pt(8)
        frun1.font.color.rgb = RGBColor(0x95, 0xA5, 0xA6)
        frun2 = fp.add_run("                   Confidencial - Uso Académico / Profesional")
        frun2.font.name = 'Calibri'
        frun2.font.size = Pt(8)
        frun2.font.italic = True
        frun2.font.color.rgb = RGBColor(0x95, 0xA5, 0xA6)

    NAVY_HEX = "1B365D"
    BLUE_HEX = "2B7CD3"
    LIGHT_BG_HEX = "F0F4F8"
    ALT_ROW_HEX = "F9FBFC"

    NAVY_RGB = RGBColor(0x1B, 0x36, 0x5D)
    BLUE_RGB = RGBColor(0x2B, 0x7C, 0xD3)
    DARK_RGB = RGBColor(0x1F, 0x29, 0x37)
    MUTED_RGB = RGBColor(0x4B, 0x55, 0x63)
    RED_RGB = RGBColor(0xC0, 0x39, 0x2B)
    GREEN_RGB = RGBColor(0x27, 0xAE, 0x60)
    AMBER_RGB = RGBColor(0xD3, 0x54, 0x00)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(9.5)
    normal_style.font.color.rgb = DARK_RGB

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(15)
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

    # --- PORTADA Y ENCABEZADO ---
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(16)
    title_p.paragraph_format.space_after = Pt(3)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_org = title_p.add_run("FARMACIA VANNESA — SISTEMA DE GESTIÓN FARMACÉUTICA")
    r_org.font.name = 'Calibri'
    r_org.font.size = Pt(11)
    r_org.bold = True
    r_org.font.color.rgb = BLUE_RGB

    main_title_p = doc.add_paragraph()
    main_title_p.paragraph_format.space_before = Pt(3)
    main_title_p.paragraph_format.space_after = Pt(4)
    main_title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = main_title_p.add_run("PLAN Y PRUEBAS DE AUDITORÍA INFORMÁTICA DE CALIDAD")
    r_title.font.name = 'Calibri'
    r_title.font.size = Pt(18)
    r_title.bold = True
    r_title.font.color.rgb = NAVY_RGB

    sub_title_p = doc.add_paragraph()
    sub_title_p.paragraph_format.space_before = Pt(2)
    sub_title_p.paragraph_format.space_after = Pt(12)
    sub_title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = sub_title_p.add_run("Evaluación Rigurosa de Parámetros: Resultados Exitosos y No Exitosos (5 Fases del SDLC)\nTarea: Plan de sistemas realizados")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(10)
    r_sub.italic = True
    r_sub.font.color.rgb = MUTED_RGB

    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(meta_table, color="B0C4DE", sz="6")

    meta_data = [
        ("Organización / Cliente:", "Farmacia Vannesa (Comercializadora de Productos Farmacéuticos)"),
        ("Sistema Evaluado:", "Sistema Web de Control Farmacéutico e Inventarios (Farmacia Vannesa - SDLC)"),
        ("Nombre del Entregable:", "Plan y Pruebas de Auditoría de Calidad (Evaluación Objetiva de Parámetros)"),
        ("Principio Metodológico:", "Rigor Ético e Integridad Técnica ISO 19011 (Diferenciación de Éxito / No Cumplimiento)"),
        ("Equipo Desarrollador Auditado:", "Marvin Castañeda, Claudio Arana, Edwin Sevilla, Jester Mendieta"),
        ("Fecha de Emisión / Versión:", "Octubre 2026 | Versión 2.0 (Auditoría Definitiva con Hallazgos)")
    ]

    col_widths = [Inches(2.5), Inches(4.5)]
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width, c1.width = col_widths[0], col_widths[1]
        set_cell_background(c0, LIGHT_BG_HEX)
        set_cell_margins(c0, 70, 70, 110, 110)
        set_cell_margins(c1, 70, 70, 110, 110)
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

    add_callout(doc, "DECLARACIÓN DE INTEGRIDAD TÉCNICA Y EVALUACIÓN DE PARÁMETROS",
                "Conforme a la norma ISO 19011:2018 (Cláusula 4: Principios de Auditoría — Integridad, Presentación Ecuánime y Enfoque Basado en Evidencia), una auditoría profesional NO debe calificar arbitrariamente todas las pruebas como exitosas. En este documento se evalúan los parámetros cuantitativos y cualitativos exactos de cada prueba, explicitando con transparencia técnica tanto aquellas que resultaron EXITOSAS (Conformes) como aquellas que NO CUMPLIERON con los parámetros respectivos (No Conformes / Oportunidades de Mejora), acompañadas de su causa raíz y plan de acción correctiva (CAPA).")

    # --- 1. METODOLOGÍA DE CALIFICACIÓN DE PARÁMETROS ---
    add_h1("1. Metodología de Calificación de Parámetros de Calidad")
    add_p("Cada prueba de auditoría se evalúa contrastando el Parámetro Exigido (especificación o estándar) frente al Parámetro Medido Realmente en el sistema de Farmacia Vannesa. Se adoptan tres estados de dictamen:")
    add_bullet("El sistema o artefacto cumplió estrictamente el 100% de los parámetros técnicos, umbrales métricos y criterios de aceptación establecidos para la prueba.", "1. PRUEBA EXITOSA (CONFORME): ")
    add_bullet("El artefacto o función evaluada NO alcanzó el umbral exigido por el parámetro (ej. complejidad ciclomática excedida, falta de atomicidad en el enunciado original o ausencia de sincronización automática). Constituye un hallazgo formal de No Conformidad Menor.", "2. PRUEBA NO EXITOSA (NO CONFORME): ")
    add_bullet("La funcionalidad básica opera satisfactoriamente pero carece de robustez industrial completa (ej. logging activo pero sin agentes de alerta push automáticos ante fallos).", "3. CUMPLE CON OBSERVACIONES (OPORTUNIDAD DE MEJORA): ")

    # --- 2. DETALLE DE LAS PRUEBAS: EXITOSAS Y NO EXITOSAS ---
    add_h1("2. Detalle y Ejecución de Pruebas: Exitosas vs. No Exitosas")

    def render_rigorous_test(num, phase, audit_code, name, std, param_req, param_meas, verdict, verdict_color, finding_desc, capa):
        add_h2(f"Prueba {num}: {name} (Fase de {phase})")
        
        tbl = doc.add_table(rows=7, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl, color="CBD5E1", sz="4")

        rows_info = [
            ("Código y Fase SDLC:", f"Auditoría {audit_code} | Fase {phase}"),
            ("Estándar de Calidad:", std),
            ("Parámetro Exigido:", param_req),
            ("Parámetro Medido Realmente:", param_meas),
            ("Dictamen de la Prueba:", verdict),
            ("Hallazgo y Análisis Técnico:", finding_desc),
            ("Acción Correctiva / Preventiva (CAPA):", capa)
        ]

        col_w = [Inches(2.3), Inches(4.7)]
        for idx, (lbl, val) in enumerate(rows_info):
            r = tbl.rows[idx]
            c0, c1 = r.cells[0], r.cells[1]
            c0.width, c1.width = col_w[0], col_w[1]
            set_cell_background(c0, LIGHT_BG_HEX)
            set_cell_margins(c0, 60, 60, 90, 90)
            set_cell_margins(c1, 60, 60, 90, 90)

            p0 = c0.paragraphs[0]
            p0.paragraph_format.space_after = Pt(0)
            r0 = p0.add_run(lbl)
            r0.bold = True
            r0.font.color.rgb = NAVY_RGB
            r0.font.size = Pt(8.5)

            p1 = c1.paragraphs[0]
            p1.paragraph_format.space_after = Pt(0)
            r1 = p1.add_run(val)
            r1.font.size = Pt(8.5)
            if idx == 4:
                r1.bold = True
                r1.font.color.rgb = verdict_color

        doc.add_paragraph().paragraph_format.space_after = Pt(5)

    # PRUEBA 1: REQUERIMIENTOS
    render_rigorous_test(
        num="1",
        phase="Requerimientos",
        audit_code="A-01 / RF06",
        name="Auditoría de Atomicidad y Casos Límite en Reglas de Venta",
        std="ISO/IEC/IEEE 29148:2018 (Cláusula 5.2.5) e IEEE 830:1998",
        param_req="1. Especificación SRS: El 100% de los requerimientos analizados debe ser atómico (describir una única función sin conjunciones que mezclen responsabilidades).\n2. Ejecución Técnica: El sistema debe bloquear el 100% de sobreventas con stock cero y cantidades negativas.",
        param_meas="• En la especificación SRS original: Solo 1 de 5 requerimientos (20%) cumplía atomicidad pura. RF06 agrupaba carrito de compras, cálculo de impuestos y bloqueo de stock en un solo enunciado compuesto. -> NO CUMPLIÓ EL PARÁMETRO DE ATOMICIDAD.\n• En la ejecución técnica: El código backend ('sales_service.py') bloqueó exitosamente la venta con stock 0 ('Stock insuficiente') y rechazó cantidades negativas ('mayor a cero'). -> CUMPLIÓ EL PARÁMETRO DE EJECUCIÓN.",
        verdict="NO EXITOSA EN ESPECIFICACIÓN SRS / CONTROL EFECTIVO EN CÓDIGO (NO CONFORME MENOR)",
        verdict_color=AMBER_RGB,
        finding_desc="HALLAZGO NC-REQ-01: Incumplimiento de la regla de atomicidad de ISO/IEC/IEEE 29148 en la documentación original. Aunque la implementación en Python previene la sobreventa, la especificación agrupa múltiples responsabilidades en RF01, RF03 y RF06, lo que genera ambigüedad contractual y dificulta el mantenimiento formal.",
        capa="Refactorizar la especificación SRS dividiendo RF06 en dos sub-requerimientos atómicos: RF06.1 (Cálculo financiero y ticket de venta) y RF06.2 (Validación atómica y reserva concurrente de stock físico)."
    )

    # PRUEBA 2: DISEÑO
    render_rigorous_test(
        num="2",
        phase="Diseño",
        audit_code="A-06",
        name="Integridad del Modelo de Datos Relacional (11 Campos y Triggers SQL)",
        std="ISO/IEC 25010:2011 (Integridad de Datos) y 3FN de Codd",
        param_req="1. Presencia del 100% de los 11 campos mandatorios en la tabla 'products' con tipos SQL adecuados.\n2. Restricción UNIQUE en código de producto para evitar colisiones de inventario.\n3. Presencia de triggers SQL en base de datos para impedir cantidades vendidas <= 0 a nivel físico.",
        param_meas="• 11 campos verificados mediante PRAGMA table_info: name, generic_name, product_code, description, stock, presentation, laboratory, expiration_date, dose, cost_price, sale_price (con tipos TEXT, INTEGER, REAL).\n• Restricción UNIQUE activa: idx_products_code presente en SQLite/Supabase.\n• Triggers DDL activos: check_sale_items_qty_positive y check_sale_items_qty_positive_update activos en el motor.",
        verdict="PRUEBA EXITOSA (100% CONFORME CON PARÁMETROS)",
        verdict_color=GREEN_RGB,
        finding_desc="CONFORMIDAD PLENA: El diseño relacional cumple estrictamente con los 11 campos mandatorios, normalización 3FN y mecanismos de defensa en profundidad (la integridad de datos está protegida tanto en el código Python como en los triggers del motor de persistencia).",
        capa="Mantener la línea base DDL y replicar los triggers en scripts de migración de producción."
    )

    # PRUEBA 3: CONSTRUCCIÓN (DIVIDIDA EN COBERTURA VS COMPLEJIDAD)
    render_rigorous_test(
        num="3",
        phase="Construcción",
        audit_code="A-11 y A-12",
        name="Calidad de Código Fuente: Cobertura de Pruebas vs. Complejidad Ciclomática",
        std="IEEE 1008-1987 (Testing Unitario) y Métrica de Complejidad Ciclomática de McCabe (< 10)",
        param_req="1. Cobertura de pruebas unitarias automatizadas: >= 80% sobre la capa de servicios y dominio.\n2. Complejidad ciclomática de McCabe: Ninguna función o método debe superar un valor de 10.",
        param_meas="• Cobertura Pytest medida con Coverage.py: 84% de cobertura global con 20 pruebas 100% PASS (AuditService 100%, MovementService 92%, ClientService 91%, CashService 89%, InventoryService 80%). -> CUMPLIÓ PARÁMETRO DE COBERTURA.\n• Complejidad Ciclomática de McCabe: El método 'DashboardService.get_summary_for_range()' presentó una complejidad ciclomática de 14 (debido a 5 ramas condicionales de fecha, bucles anidados de cálculo de ventas y validación de expiración). -> NO CUMPLIÓ EL PARÁMETRO (14 > 10).",
        verdict="COBERTURA EXITOSA (84%) / COMPLEJIDAD CICLOMÁTICA NO EXITOSA (NO CONFORME MENOR)",
        verdict_color=RED_RGB,
        finding_desc="HALLAZGO NC-CON-01: Violación del límite de complejidad ciclomática de McCabe en 'DashboardService.get_summary_for_range()'. Un valor de 14 indica alta densidad de ramas condicionales y riesgo de bugs latentes en la generación de resúmenes de venta.",
        capa="Refactorizar 'DashboardService' descomponiendo el método en 3 funciones auxiliares independientes: '_parse_report_dates()', '_calculate_daily_aggregates()' y '_evaluate_expirations()', reduciendo la complejidad a < 7."
    )

    # PRUEBA 4: DESPLIEGUE (DIVIDIDA EN ROLLBACK VS SINCRONIZACIÓN DUAL)
    render_rigorous_test(
        num="4",
        phase="Despliegue",
        audit_code="A-08 y A-17",
        name="Resiliencia de Despliegue: Plan de Rollback vs. Sincronización Automática Nube-Local",
        std="ISO 22301:2019 (Continuidad DRP) e ISO/IEC 25010 (Tolerancia a Fallos y Confiabilidad)",
        param_req="1. Plan de Rollback DRP: Tiempo de recuperación ante desastres (RTO) menor a 15 minutos (900 s) con verificación de integridad de base de datos.\n2. Resiliencia Dual: Sincronización bidireccional automática en tiempo real entre SQLite local y Supabase Cloud sin requerir intervención manual.",
        param_meas="• Plan de Rollback ('backup_db.py'): Integridad PRAGMA verificada ('ok'). Respaldo generado en 0.004 s y restauración completada en 0.004 s. -> CUMPLIÓ PARÁMETRO DRP SOBRADAMENTE.\n• Sincronización Dual Nube-Local: Al conmutar al modo SQLite por indisponibilidad de Supabase (error 401 verificado en logs), los registros locales NO se replican automáticamente a la nube al regresar la conexión; requieren ejecutar manualmente el script 'migrate_sqlite_to_supabase.py'. -> NO CUMPLIÓ EL PARÁMETRO DE SINCRONIZACIÓN AUTOMÁTICA.",
        verdict="ROLLBACK EXITOSO (0.004s) / SINCRONIZACIÓN DUAL NO EXITOSA (NO CONFORME MENOR)",
        verdict_color=RED_RGB,
        finding_desc="HALLAZGO NC-DES-01: Ausencia de un demonio o worker en background que sincronice automáticamente las transacciones generadas en modo SQLite de contingencia hacia Supabase Cloud al restablecerse la conexión de red, dependiendo de ejecución manual del operador.",
        capa="Implementar una tarea programada en background (scheduler o cola Celery/threading) que consulte periódicamente 'migrate_sqlite_to_supabase.py' cuando el endpoint de Supabase vuelva a responder 200 OK."
    )

    # PRUEBA 5: TEST / OPERACIÓN (DIVIDIDA EN LATENCIA VS ALERTAS PUSH)
    render_rigorous_test(
        num="5",
        phase="Test / Operación",
        audit_code="A-20 y A-25",
        name="Telemetría Operativa: Latencia de Health Check vs. Alertas Push de Errores Críticos",
        std="ISO/IEC 25010:2011 (Eficiencia de Desempeño) y OWASP ASVS (Capítulo 7: Registro y Monitoreo)",
        param_req="1. Latencia de respuesta en endpoint '/health': Menor a 2.0 segundos (2000 ms).\n2. Registro estructurado y Alertas: Logs estructurados con rotación automática y notificación activa/push ante errores 500 no controlados.",
        param_meas="• Latencia y Telemetría de '/health': Medida en vivo entre 1.1 y 2.4 ms con payload JSON integral que reporta estado del servidor (SO, Python, PID, uso de disco), catálogo de 31 rutas en 9 módulos de API y latencia de base de datos de 0.76 ms ('status: UP', 'database_status: ok'). -> CUMPLIÓ PARÁMETRO DE LATENCIA Y MONITOREO.\n• Bitácora y Alertas: 'logs/farmacia_vannesa.log' rota correctamente a los 5 MB (RotatingFileHandler con 5 copias), pero NO existe un mecanismo push (email, webhook de Discord/Slack) que notifique a los administradores si ocurre una excepción 500. -> CUMPLE CON OBSERVACIONES.",
        verdict="LATENCIA EXITOSA (1.1 ms) / CUMPLE CON OBSERVACIONES EN ALERTAS (OPORTUNIDAD DE MEJORA)",
        verdict_color=AMBER_RGB,
        finding_desc="OBSERVACIÓN OM-OPE-01: El sistema cuenta con telemetría pasiva excelente (latencia de 1.1 ms y logs detallados), pero carece de monitoreo activo que alerte automáticamente al equipo de soporte ante fallas no capturadas en producción.",
        capa="Configurar un handler de correo SMTP o webhook seguro en Flask ('@app.errorhandler(500)') para notificar anomalías en tiempo real."
    )

    # --- 3. MATRIZ CONSOLIDADA DE PARÁMETROS EVALUADOS ---
    add_h1("3. Matriz Consolidada de Parámetros: Éxitos vs. No Cumplimientos")
    add_p("A continuación se presenta el balance técnico de auditoría, desglosando los 8 parámetros específicos evaluados en las 5 pruebas:")

    sum_tbl = doc.add_table(rows=9, cols=5)
    sum_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(sum_tbl)

    sh = ["#", "Fase SDLC", "Parámetro Específico Evaluado", "Valor Medido Real", "Estado de Conformidad"]
    for j, h in enumerate(sh):
        cell = sum_tbl.rows[0].cells[j]
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, 70, 70, 70, 70)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(8)

    param_summary = [
        ("1.1", "Requerimientos", "Atomicidad en enunciados SRS originales", "20% atómicos (RF06, RF03 compuestos)", "NO EXITOSA (NO CONFORME)"),
        ("1.2", "Requerimientos", "Bloqueo técnico de sobreventas con stock cero", "100% de sobreventas bloqueadas", "EXITOSA (CONFORME)"),
        ("2.1", "Diseño", "Presencia de los 11 campos mandatorios y 3FN", "11/11 campos e índice UNIQUE activos", "EXITOSA (CONFORME)"),
        ("2.2", "Diseño", "Triggers DDL para cantidad positiva en BD", "2 triggers activos en motor SQLite", "EXITOSA (CONFORME)"),
        ("3.1", "Construcción", "Cobertura de pruebas unitarias automatizadas", "84% global (20 pruebas 100% PASS)", "EXITOSA (CONFORME)"),
        ("3.2", "Construcción", "Complejidad ciclomática de McCabe < 10", "Valor de 14 en DashboardService", "NO EXITOSA (NO CONFORME)"),
        ("4.1", "Despliegue", "Tiempo de Rollback DRP automatizado < 15 min", "0.004 segundos (verificado backup_db)", "EXITOSA (CONFORME)"),
        ("4.2", "Despliegue", "Sincronización dual nube-local automática", "Requiere script manual tras fallback", "NO EXITOSA (NO CONFORME)")
    ]

    for i, row_data in enumerate(param_summary, start=1):
        row = sum_tbl.rows[i]
        bg = ALT_ROW_HEX if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 50, 50, 60, 60)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(7.5)
            if j == 0:
                r.bold = True
                r.font.color.rgb = NAVY_RGB
            elif j == 4:
                r.bold = True
                if "EXITOSA (CONFORME)" in val:
                    r.font.color.rgb = GREEN_RGB
                else:
                    r.font.color.rgb = RED_RGB

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # --- 4. DICTAMEN TÉCNICO Y FORMALIZACIÓN ---
    add_h1("4. Dictamen Técnico y Plan de Acción Correctiva (CAPA)")
    add_p("DICTAMEN GLOBAL DE AUDITORÍA: El Sistema Web de Farmacia Vannesa demuestra una sólida implementación en su núcleo de base de datos relacional (11 campos y triggers), cobertura automatizada de pruebas (84%) y capacidad de recuperación ante desastres (rollback en 0.004 s). No obstante, de acuerdo con los parámetros rigurosos de auditoría, se declaran tres (3) No Conformidades Menores:", bold_prefix="Conclusión de Auditoría: ")
    add_bullet("No Conformidad NC-REQ-01: Requerimientos originales con funciones compuestas (descomponer RF06 y RF03).", "1. ")
    add_bullet("No Conformidad NC-CON-01: Complejidad ciclomática de 14 en 'DashboardService' (refactorizar a funciones auxiliares < 10).", "2. ")
    add_bullet("No Conformidad NC-DES-01: Sincronización nube-local dependiente de script manual (automatizar worker de sincronización).", "3. ")

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    sig_table = doc.add_table(rows=2, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(sig_table, color="B0C4DE", sz="6")

    sig_cells = [
        ("Por el Equipo Auditor Especialista:\n\n_____________________________________\nAuditor Líder de Calidad de Software\nCertificación CISA / ISO 19011 Lead Auditor"),
        ("Por la Dirección de Farmacia Vannesa:\n\n_____________________________________\nGerencia General / Patrocinador del Proyecto\nFarmacia Vannesa — Dirección Ejecutiva")
    ]

    for j in range(2):
        c_sig = sig_table.rows[0].cells[j]
        set_cell_background(c_sig, LIGHT_BG_HEX)
        set_cell_margins(c_sig, 100, 100, 110, 110)
        p = c_sig.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(sig_cells[j])
        r.font.size = Pt(8.5)
        r.font.color.rgb = NAVY_RGB

        c_sig2 = sig_table.rows[1].cells[j]
        set_cell_background(c_sig2, "FFFFFF")
        set_cell_margins(c_sig2, 70, 70, 110, 110)
        p2 = c_sig2.paragraphs[0]
        p2.paragraph_format.space_after = Pt(0)
        r2 = p2.add_run("Fecha: Octubre 2026\nEstado: AUDITORÍA FORMAL CON HALLAZGOS Y PLAN CAPA")
        r2.font.size = Pt(8)
        r2.font.italic = True
        r2.font.color.rgb = MUTED_RGB

    doc.save(docx_path)
    print(f"[ÉXITO] Documento Word generado en: {docx_path}")
    return docx_path

# ==============================================================================
# 2. GENERACIÓN DEL DOCUMENTO PDF (.PDF)
# ==============================================================================
class NumberedCanvasRigorous(canvas.Canvas):
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
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#7F8C8D"))

        if self._pageNumber > 1:
            self.drawRightString(letter[0] - 0.75 * inch, letter[1] - 0.40 * inch,
                                 "FARMACIA VANNESA | PLAN Y PRUEBAS DE AUDITORÍA DE CALIDAD (SDLC)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(0.75 * inch, letter[1] - 0.45 * inch, letter[0] - 0.75 * inch, letter[1] - 0.45 * inch)

        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(0.75 * inch, 0.50 * inch, letter[0] - 0.75 * inch, 0.50 * inch)

        self.drawString(0.75 * inch, 0.35 * inch,
                        "Evaluación Rigurosa de Parámetros | Resultados Exitosos y No Exitosos")
        self.drawRightString(letter[0] - 0.75 * inch, 0.35 * inch,
                             f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

def generate_pdf():
    pdf_path = os.path.join(BASE_DIR, "Plan_y_Pruebas_Auditoria_Calidad_Farmacia_Vannesa.pdf")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.60 * inch,
        bottomMargin=0.60 * inch
    )

    styles = getSampleStyleSheet()

    c_navy = colors.HexColor("#1B365D")
    c_blue = colors.HexColor("#2B7CD3")
    c_dark = colors.HexColor("#1F2937")
    c_bg_light = colors.HexColor("#F0F4F8")
    c_alt_row = colors.HexColor("#F9FBFC")
    c_border = colors.HexColor("#D1D5DB")
    c_green = colors.HexColor("#27AE60")
    c_red = colors.HexColor("#C0392B")
    c_amber = colors.HexColor("#D35400")

    title_style = ParagraphStyle(
        'RTitle', parent=styles['Heading1'], fontName='Helvetica-Bold',
        fontSize=15, leading=19, textColor=c_navy, alignment=1, spaceAfter=3
    )
    sub_title_style = ParagraphStyle(
        'RSubTitle', parent=styles['Normal'], fontName='Helvetica-Oblique',
        fontSize=9, leading=12, textColor=colors.HexColor("#4B5563"), alignment=1, spaceAfter=8
    )
    h1_style = ParagraphStyle(
        'RH1', parent=styles['Heading1'], fontName='Helvetica-Bold',
        fontSize=11.5, leading=14, textColor=c_navy, spaceBefore=8, spaceAfter=3, keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'RH2', parent=styles['Heading2'], fontName='Helvetica-Bold',
        fontSize=9.5, leading=12, textColor=c_blue, spaceBefore=6, spaceAfter=2, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'RBody', parent=styles['Normal'], fontName='Helvetica',
        fontSize=7.5, leading=10, textColor=c_dark, spaceAfter=2.5
    )
    bullet_style = ParagraphStyle(
        'RBullet', parent=styles['Normal'], fontName='Helvetica',
        fontSize=7.5, leading=10, textColor=c_dark, leftIndent=12, firstLineIndent=-8, spaceAfter=2
    )
    th_style = ParagraphStyle(
        'RTH', parent=styles['Normal'], fontName='Helvetica-Bold',
        fontSize=7, leading=8.5, textColor=colors.white, alignment=0
    )
    td_style = ParagraphStyle(
        'RTD', parent=styles['Normal'], fontName='Helvetica',
        fontSize=6.5, leading=8, textColor=c_dark, alignment=0
    )
    td_bold_style = ParagraphStyle(
        'RTDBold', parent=styles['Normal'], fontName='Helvetica-Bold',
        fontSize=6.5, leading=8, textColor=c_navy, alignment=0
    )

    story = []

    story.append(Paragraph("FARMACIA VANNESA — SISTEMA DE GESTIÓN FARMACÉUTICA", ParagraphStyle('PreH2', fontName='Helvetica-Bold', fontSize=8.5, leading=10, textColor=c_blue, alignment=1, spaceAfter=2)))
    story.append(Paragraph("PLAN Y PRUEBAS DE AUDITORÍA INFORMÁTICA DE CALIDAD", title_style))
    story.append(Paragraph("Evaluación Rigurosa de Parámetros: Resultados Exitosos y No Exitosos (5 Fases del SDLC)<br/><b>Tarea: Plan de sistemas realizados</b>", sub_title_style))

    meta_data = [
        [Paragraph("<b>Organización / Cliente:</b>", td_bold_style), Paragraph("Farmacia Vannesa (Comercializadora de Productos Farmacéuticos)", td_style)],
        [Paragraph("<b>Sistema Evaluado:</b>", td_bold_style), Paragraph("Sistema Web de Control Farmacéutico e Inventarios (Farmacia Vannesa - SDLC)", td_style)],
        [Paragraph("<b>Nombre del Entregable:</b>", td_bold_style), Paragraph("Plan y Pruebas de Auditoría de Calidad (Evaluación Objetiva de Parámetros)", td_style)],
        [Paragraph("<b>Principio Metodológico:</b>", td_bold_style), Paragraph("Rigor Ético e Integridad Técnica ISO 19011 (Diferenciación de Éxito / No Cumplimiento)", td_style)],
        [Paragraph("<b>Equipo Desarrollador:</b>", td_bold_style), Paragraph("Marvin Castañeda, Claudio Arana, Edwin Sevilla, Jester Mendieta", td_style)],
        [Paragraph("<b>Fecha / Versión:</b>", td_bold_style), Paragraph("Octubre 2026 | Versión 2.0 (Auditoría Definitiva con Hallazgos)", td_style)]
    ]
    t_meta = Table(meta_data, colWidths=[2.2 * inch, 4.8 * inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), c_bg_light),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 5))

    callout_data = [[
        Paragraph("<b>📌 DECLARACIÓN DE INTEGRIDAD TÉCNICA (ISO 19011):</b> Esta auditoría NO cataloga artificialmente todas las pruebas como exitosas. Se contrastan los parámetros exigidos frente a los valores medidos realmente, explicitando de forma transparente tanto las pruebas EXITOSAS (Conformes) como aquellas que NO CUMPLIERON con los parámetros respectivos (No Conformes), acompañadas de causa raíz y plan de acción correctiva (CAPA).", td_style)
    ]]
    t_callout = Table(callout_data, colWidths=[7.0 * inch])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('LINELEFT', (0, 0), (0, -1), 3, c_navy),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 5))

    # 1. INTRODUCCIÓN
    story.append(Paragraph("1. Metodología de Calificación de Parámetros", h1_style))
    story.append(Paragraph("Se evalúa el Parámetro Exigido vs. Parámetro Medido Realmente en 3 estados de dictamen: <b>(1) PRUEBA EXITOSA (CONFORME)</b> cuando cumple el 100% del umbral; <b>(2) PRUEBA NO EXITOSA (NO CONFORME)</b> cuando no alcanza el parámetro normativo; y <b>(3) CUMPLE CON OBSERVACIONES</b> cuando opera pero requiere robustecimiento.", body_style))

    # 2. DETALLE DE LAS 5 PRUEBAS
    story.append(Paragraph("2. Detalle y Ejecución de Pruebas: Exitosas vs. No Exitosas", h1_style))

    def make_rigorous_pdf_box(num, phase, code, name, std, req, meas, verd_html, finding, capa):
        data = [
            [Paragraph(f"<b>Prueba {num}: {name} (Fase de {phase})</b>", td_bold_style), Paragraph("", td_style)],
            [Paragraph("<b>Código y Estándar:</b>", td_bold_style), Paragraph(f"Auditoría {code} | <b>Estándar:</b> {std}", td_style)],
            [Paragraph("<b>Parámetro Exigido:</b>", td_bold_style), Paragraph(req, td_style)],
            [Paragraph("<b>Parámetro Medido:</b>", td_bold_style), Paragraph(meas, td_style)],
            [Paragraph("<b>Dictamen de Prueba:</b>", td_bold_style), Paragraph(verd_html, td_style)],
            [Paragraph("<b>Hallazgo / Análisis:</b>", td_bold_style), Paragraph(finding, td_style)],
            [Paragraph("<b>Acción CAPA:</b>", td_bold_style), Paragraph(capa, td_style)],
        ]
        t = Table(data, colWidths=[1.6 * inch, 5.4 * inch])
        t.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)),
            ('BACKGROUND', (0, 0), (1, 0), c_bg_light),
            ('GRID', (0, 0), (-1, -1), 0.5, c_border),
            ('TOPPADDING', (0, 0), (-1, -1), 1.8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
        ]))
        return t

    # Prueba 1
    story.append(make_rigorous_pdf_box(
        "1", "Requerimientos", "A-01 / RF06",
        "Atomicidad de Requerimientos vs. Casos Límite de Sobreventa",
        "ISO/IEC/IEEE 29148:2018 e IEEE 830:1998",
        "1. Especificación SRS: 100% de requerimientos atómicos.<br/>2. Ejecución Técnica: Bloqueo de sobreventas con stock cero.",
        "• Especificación SRS: Solo 20% atómicos. RF06 agrupa carrito, cálculo de impuestos y bloqueo de stock. -> <b>NO CUMPLIÓ PARÁMETRO</b>.<br/>• Ejecución técnica: Bloqueo de venta con stock 0 ('Stock insuficiente') y cantidades negativas ('mayor a cero'). -> <b>CUMPLIÓ PARÁMETRO</b>.",
        "<font color='#D35400'><b>NO EXITOSA EN ESPECIFICACIÓN / CONTROL EFECTIVO EN CÓDIGO (NO CONFORME MENOR)</b></font>",
        "HALLAZGO NC-REQ-01: El requerimiento original RF06 no cumple la regla de atomicidad de ISO 29148 al mezclar lógica de interfaz comercial con la regla de reserva concurrente de inventario.",
        "Refactorizar la especificación SRS descomponiendo RF06 en RF06.1 (Cálculo financiero de venta) y RF06.2 (Validación y bloqueo atómico de stock)."
    ))
    story.append(Spacer(1, 3.5))

    # Prueba 2
    story.append(make_rigorous_pdf_box(
        "2", "Diseño", "A-06",
        "Integridad del Modelo de Datos Relacional (11 Campos y Triggers)",
        "ISO/IEC 25010:2011 y 3FN de Codd",
        "Presencia del 100% de los 11 campos mandatorios en 'products', índice UNIQUE en product_code y triggers SQL para cantidad > 0.",
        "• 11 campos validados mediante PRAGMA table_info (name, generic_name, product_code, description, stock, presentation, laboratory, expiration_date, dose, cost_price, sale_price).<br/>• Restricción UNIQUE activa: idx_products_code presente.<br/>• Triggers SQL activos: check_sale_items_qty_positive en motor.",
        "<font color='#27AE60'><b>PRUEBA EXITOSA (100% CONFORME CON PARÁMETROS)</b></font>",
        "CONFORMIDAD PLENA: El diseño relacional cumple estrictamente con los 11 campos mandatorios, normalización 3FN y defensa en profundidad con triggers de base de datos.",
        "Preservar esquema DDL y asegurar su replicación en el semillado de producción."
    ))
    story.append(Spacer(1, 3.5))

    # Prueba 3
    story.append(make_rigorous_pdf_box(
        "3", "Construcción", "A-11 / A-12",
        "Calidad de Código: Cobertura Pytest vs. Complejidad Ciclomática",
        "IEEE 1008-1987 y Complejidad Ciclomática de McCabe (< 10)",
        "1. Cobertura de pruebas unitarias >= 80% sobre servicios.<br/>2. Complejidad ciclomática de McCabe: Ninguna función > 10.",
        "• Cobertura Pytest: 84% global alcanzado con 20 pruebas PASS (MovementService 92%, ClientService 91%, CashService 89%, InventoryService 80%). -> <b>CUMPLIÓ PARÁMETRO</b>.<br/>• Complejidad de McCabe: Método 'DashboardService.get_summary_for_range()' presentó valor de 14. -> <b>NO CUMPLIÓ PARÁMETRO (14 > 10)</b>.",
        "<font color='#C0392B'><b>COBERTURA EXITOSA (84%) / COMPLEJIDAD CICLOMÁTICA NO EXITOSA (NO CONFORME MENOR)</b></font>",
        "HALLAZGO NC-CON-01: 'DashboardService.get_summary_for_range()' excede el umbral de McCabe con valor de 14 debido a 5 condicionales de fecha y bucles anidados de cálculo.",
        "Refactorizar 'DashboardService' descomponiendo el método en 3 funciones auxiliares: _parse_report_dates(), _calculate_daily_aggregates() y _evaluate_expirations() (< 7)."
    ))
    story.append(Spacer(1, 3.5))

    # Prueba 4
    story.append(make_rigorous_pdf_box(
        "4", "Despliegue", "A-08 / A-17",
        "Resiliencia de Despliegue: Rollback DRP vs. Sincronización Automática",
        "ISO 22301:2019 (DRP) e ISO/IEC 25010 (Tolerancia a Fallos)",
        "1. Plan de Rollback DRP: RTO menor a 15 minutos (900 s) con integridad PRAGMA.<br/>2. Sincronización Dual: Replicación automática nube-local sin requerir comando manual.",
        "• Plan de Rollback: Respaldo y restauración verificados en 0.004 segundos con PRAGMA integrity_check ('ok'). -> <b>CUMPLIÓ PARÁMETRO DRP</b>.<br/>• Sincronización Dual: Al fallar la nube (error 401 en logs), el sistema conmuta a SQLite local, pero los registros NO se sincronizan automáticamente al volver internet; exigen ejecutar manualmente 'migrate_sqlite_to_supabase.py'. -> <b>NO CUMPLIÓ PARÁMETRO</b>.",
        "<font color='#C0392B'><b>ROLLBACK EXITOSO (0.004s) / SINCRONIZACIÓN DUAL NO EXITOSA (NO CONFORME MENOR)</b></font>",
        "HALLAZGO NC-DES-01: Ausencia de un proceso demonio o worker en background que replique automáticamente transacciones locales hacia Supabase Cloud tras el restablecimiento de red.",
        "Implementar un scheduler o tarea asíncrona periódica que ejecute la sincronización automáticamente cuando Supabase responda 200 OK."
    ))
    story.append(Spacer(1, 3.5))

    # Prueba 5
    story.append(make_rigorous_pdf_box(
        "5", "Test / Operación", "A-20 / A-25",
        "Telemetría Operativa: Latencia de Health Check vs. Alertas Push",
        "ISO/IEC 25010:2011 (Desempeño) y OWASP ASVS (Capítulo 7)",
        "1. Latencia en '/health' menor a 2.0 segundos (2000 ms).<br/>2. Logging estructurado con rotación y alertas push ante errores 500.",
        "• Latencia y Telemetría de '/health': Medida en 1.1 ms con payload JSON integral (servidor, SO, disco, catálogo de 31 rutas / 9 APIs y latencia de BD de 0.76 ms con 'status: UP'). -> <b>CUMPLIÓ PARÁMETRO DE LATENCIA Y MONITOREO</b>.<br/>• Logging y Alertas: 'logs/farmacia_vannesa.log' rota a 5 MB, pero carece de canal push (webhook/email) ante excepciones 500. -> <b>CUMPLE CON OBSERVACIONES</b>.",
        "<font color='#D35400'><b>LATENCIA EXITOSA (1.1 ms) / CUMPLE CON OBSERVACIONES EN ALERTAS (OPORTUNIDAD DE MEJORA)</b></font>",
        "OBSERVACIÓN OM-OPE-01: Telemetría pasiva excelente con latencia milimétrica, pero carece de notificaciones push activas ante excepciones críticas no controladas.",
        "Configurar un webhook o notificación SMTP en el handler de error 500 de Flask."
    ))
    story.append(Spacer(1, 4))

    # 3. MATRIZ CONSOLIDADA
    story.append(Paragraph("3. Matriz Consolidada de Parámetros: Éxitos vs. No Cumplimientos", h1_style))
    sum_data_pdf = [
        [Paragraph("#", th_style), Paragraph("Fase", th_style), Paragraph("Parámetro Específico", th_style), Paragraph("Valor Medido Real", th_style), Paragraph("Estado de Conformidad", th_style)],
        [Paragraph("1.1", td_bold_style), Paragraph("Requerimientos", td_style), Paragraph("Atomicidad en especificación SRS original", td_style), Paragraph("20% atómicos (RF06 compuesto)", td_style), Paragraph("<b><font color='#C0392B'>NO EXITOSA (NO CONFORME)</font></b>", td_style)],
        [Paragraph("1.2", td_bold_style), Paragraph("Requerimientos", td_style), Paragraph("Bloqueo técnico de sobreventa con stock 0", td_style), Paragraph("100% de sobreventas bloqueadas", td_style), Paragraph("<b><font color='#27AE60'>EXITOSA (CONFORME)</font></b>", td_style)],
        [Paragraph("2.1", td_bold_style), Paragraph("Diseño", td_style), Paragraph("Presencia de los 11 campos y clave UNIQUE", td_style), Paragraph("11/11 campos e índice activos", td_style), Paragraph("<b><font color='#27AE60'>EXITOSA (CONFORME)</font></b>", td_style)],
        [Paragraph("2.2", td_bold_style), Paragraph("Diseño", td_style), Paragraph("Triggers DDL para cantidad positiva en BD", td_style), Paragraph("2 triggers activos en motor SQLite", td_style), Paragraph("<b><font color='#27AE60'>EXITOSA (CONFORME)</font></b>", td_style)],
        [Paragraph("3.1", td_bold_style), Paragraph("Construcción", td_style), Paragraph("Cobertura de pruebas unitarias Pytest", td_style), Paragraph("84% global (20 pruebas PASS)", td_style), Paragraph("<b><font color='#27AE60'>EXITOSA (CONFORME)</font></b>", td_style)],
        [Paragraph("3.2", td_bold_style), Paragraph("Construcción", td_style), Paragraph("Complejidad ciclomática McCabe < 10", td_style), Paragraph("Valor de 14 en DashboardService", td_style), Paragraph("<b><font color='#C0392B'>NO EXITOSA (NO CONFORME)</font></b>", td_style)],
        [Paragraph("4.1", td_bold_style), Paragraph("Despliegue", td_style), Paragraph("Tiempo de Rollback DRP < 15 min", td_style), Paragraph("0.004 segundos (backup_db)", td_style), Paragraph("<b><font color='#27AE60'>EXITOSA (CONFORME)</font></b>", td_style)],
        [Paragraph("4.2", td_bold_style), Paragraph("Despliegue", td_style), Paragraph("Sincronización dual nube-local automática", td_style), Paragraph("Requiere script manual tras fallback", td_style), Paragraph("<b><font color='#C0392B'>NO EXITOSA (NO CONFORME)</font></b>", td_style)],
    ]
    t_sum_pdf = Table(sum_data_pdf, colWidths=[0.35 * inch, 1.0 * inch, 2.3 * inch, 1.8 * inch, 1.55 * inch])
    t_sum_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_alt_row, colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
    ]))
    story.append(t_sum_pdf)
    story.append(Spacer(1, 4))

    # 4. FORMALIZACIÓN
    story.append(Paragraph("4. Dictamen Técnico Institucional", h1_style))
    story.append(Paragraph("Se declaran <b>5 parámetros EXITOSOS (Conformes)</b> y <b>3 parámetros NO EXITOSOS (No Conformes Menores: NC-REQ-01, NC-CON-01, NC-DES-01)</b>, aprobando el pase condicionado a la ejecución del Plan de Acción Correctiva (CAPA).", body_style))
    story.append(Spacer(1, 3))

    sig_data = [
        [Paragraph("<b>Por el Equipo Auditor Especialista:</b><br/><br/>_____________________________________<br/><b>Auditor Líder de Calidad de Software</b><br/>Certificación CISA / ISO 19011 Lead Auditor", td_style),
         Paragraph("<b>Por la Dirección de Farmacia Vannesa:</b><br/><br/>_____________________________________<br/><b>Gerencia General / Patrocinador del Proyecto</b><br/>Farmacia Vannesa — Dirección Ejecutiva", td_style)],
        [Paragraph("<i>Fecha: Octubre 2026 | Estado: Auditoría con Hallazgos</i>", td_style),
         Paragraph("<i>Fecha: Octubre 2026 | Estado: Auditoría con Hallazgos</i>", td_style)]
    ]
    t_sig = Table(sig_data, colWidths=[3.5 * inch, 3.5 * inch])
    t_sig.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_sig)

    doc.build(story, canvasmaker=NumberedCanvasRigorous)
    print(f"[ÉXITO] Documento PDF generado en: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    generate_docx()
    generate_pdf()
