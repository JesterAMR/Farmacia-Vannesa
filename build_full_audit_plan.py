# -*- coding: utf-8 -*-
"""
Script generador del documento Word (.docx) del Plan de Auditoría de Calidad
para el sistema 'Farmacia Vannesa'.
Tarea: Plan de sistemas realizados
Incorpora los 11 campos mandatorios, checklist IEEE 830, métricas cuantitativas,
procedimientos en 2 pasos operativos y tabla final de mapeo integral de auditorías.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from docx_helpers import set_cell_background, set_cell_margins, set_table_borders, add_callout

def create_document():
    doc = Document()
    
    # Márgenes de página (2.5 cm ~ 0.9 inch)
    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
        
        # Encabezado
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("FARMACIA VANNESA | PLAN DE AUDITORÍA INFORMÁTICA DE CALIDAD (SDLC)")
        hrun.font.name = 'Calibri'
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(0x7F, 0x8C, 0x8D)
        
        # Pie de página
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        frun1 = fp.add_run("Tarea: Plan de sistemas realizados | Enfoque: Calidad y Gobernanza de Software")
        frun1.font.name = 'Calibri'
        frun1.font.size = Pt(8)
        frun1.font.color.rgb = RGBColor(0x95, 0xA5, 0xA6)
        frun2 = fp.add_run("                   Confidencial - Uso Interno")
        frun2.font.name = 'Calibri'
        frun2.font.size = Pt(8)
        frun2.font.italic = True
        frun2.font.color.rgb = RGBColor(0x95, 0xA5, 0xA6)

    # Paleta de Colores
    NAVY_HEX = "1B365D"
    BLUE_HEX = "2B7CD3"
    LIGHT_BG_HEX = "F0F4F8"
    ALT_ROW_HEX = "F9FBFC"
    
    NAVY_RGB = RGBColor(0x1B, 0x36, 0x5D)
    BLUE_RGB = RGBColor(0x2B, 0x7C, 0xD3)
    DARK_RGB = RGBColor(0x1F, 0x29, 0x37)
    MUTED_RGB = RGBColor(0x4B, 0x55, 0x63)
    
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = DARK_RGB

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(13.5)
        run.bold = True
        run.font.color.rgb = NAVY_RGB
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(11)
        run.bold = True
        run.font.color.rgb = BLUE_RGB
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(10)
        run.bold = True
        run.font.color.rgb = DARK_RGB
        return p

    def add_p(text, bold_prefix=None, space_after=4):
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

    # ==========================================
    # PORTADA / METADATA INSTITUCIONAL
    # ==========================================
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(20)
    title_p.paragraph_format.space_after = Pt(4)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_org = title_p.add_run("FARMACIA VANNESA — SISTEMA DE GESTIÓN FARMACÉUTICA")
    r_org.font.name = 'Calibri'
    r_org.font.size = Pt(12)
    r_org.bold = True
    r_org.font.color.rgb = BLUE_RGB

    main_title_p = doc.add_paragraph()
    main_title_p.paragraph_format.space_before = Pt(4)
    main_title_p.paragraph_format.space_after = Pt(6)
    main_title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = main_title_p.add_run("PLAN DE AUDITORÍA INFORMÁTICA DE CALIDAD DE SISTEMAS")
    r_title.font.name = 'Calibri'
    r_title.font.size = Pt(20)
    r_title.bold = True
    r_title.font.color.rgb = NAVY_RGB

    sub_title_p = doc.add_paragraph()
    sub_title_p.paragraph_format.space_before = Pt(2)
    sub_title_p.paragraph_format.space_after = Pt(16)
    sub_title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = sub_title_p.add_run("Programa de Trabajo Detallado de 25 Auditorías del Ciclo de Vida del Software (SDLC)\nNombre de la Tarea: Plan de sistemas realizados")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(11)
    r_sub.italic = True
    r_sub.font.color.rgb = MUTED_RGB

    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(meta_table, color="B0C4DE", sz="6")
    
    meta_data = [
        ("Organización / Cliente:", "Farmacia Vannesa (Comercializadora de Productos Farmacéuticos)"),
        ("Sistema Auditado:", "Sistema Web de Control Farmacéutico e Inventarios (Farmacia Vannesa - SDLC)"),
        ("Tipo de Auditoría:", "Auditoría Informática de Calidad, Estándares de Ingeniería y Gobernanza SDLC"),
        ("Alcance Metodológico:", "5 Fases del Ciclo de Vida (25 Auditorías Técnicas con Procedimientos en 2 Pasos)"),
        ("Equipo Desarrollador Auditado:", "Marvin Castañeda, Claudio Arana, Edwin Sevilla, Jester Mendieta"),
        ("Fecha de Emisión / Versión:", "Octubre 2026 | Versión 1.0 (Plan de Trabajo Oficial)")
    ]
    
    col_widths = [Inches(2.5), Inches(4.5)]
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width, c1.width = col_widths[0], col_widths[1]
        set_cell_background(c0, LIGHT_BG_HEX)
        set_cell_margins(c0, 90, 90, 130, 130)
        set_cell_margins(c1, 90, 90, 130, 130)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.color.rgb = NAVY_RGB
        r0.font.size = Pt(9)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    add_callout(doc, "DECLARACIÓN DE ENFOQUE EXCLUSIVO EN CALIDAD Y SDLC", 
                "El presente plan atiende con rigor técnico el apartado de CALIDAD del sistema informático y su gobernanza. Evalúa las cinco (5) fases del ciclo de vida del software: Requerimientos, Diseño, Construcción, Pruebas y Despliegue, totalizando 25 auditorías operativas. Se excluyen deliberadamente auditorías de infraestructura física (servidores on-premise, racks, UPS físicos, Wi-Fi corporativo) y perimetral de hardware, garantizando un análisis profundo del software conforme a ISO/IEC 25010, IEEE 830 y CMMI-DEV.")

    # ==========================================
    # 1. GOBERNANZA DE CALIDAD DEL DESARROLLO
    # ==========================================
    add_h1("1. Gobernanza de Calidad del Desarrollo del Sistema")
    add_p("La Gobernanza de Calidad establece las directrices, responsabilidades, canales de comunicación y políticas técnicas para asegurar que el sistema satisfaga los estándares internacionales. Comprende la infraestructura metodológica y operativa bajo la cual el equipo de ingeniería concibe, construye, verifica y despliega el producto.")

    add_h2("1.1. Estructura Organizacional y Roles de Aseguramiento de Calidad (SQA)")
    add_bullet("Dirección del producto, aprobación de historias de usuario, priorización del backlog y validación de las reglas de negocio farmacéutico (11 campos mandatorios, ventas bajo receta, mermas).", "Product Owner / Líder de Dominio: ")
    add_bullet("Custodio de los principios de diseño arquitectónico (Clean Architecture), modularidad, separación del dominio respecto a Flask/Supabase y patrones de persistencia.", "Líder de Arquitectura y Seguridad: ")
    add_bullet("Responsable de la automatización de suites de prueba, definición del Definition of Done (DoD), control del umbral de cobertura (>= 80%) y análisis de valores límite.", "Líder de Calidad y Pruebas (QA Lead): ")
    add_bullet("Implementación funcional, seguimiento estricto de guías de estilo PEP 8, desarrollo guiado por pruebas unitarias y corrección de deuda técnica.", "Equipo de Construcción (Developers): ")
    add_bullet("Gestión de configuraciones seguras en .env, pipelines de validación automatizada, control de migraciones de base de datos y protocolos de rollback.", "Ingeniero DevOps / Release Manager: ")

    add_h2("1.2. Marco de Comunicación y Gestión de Incidentes de Calidad")
    add_bullet("Reuniones de 15 minutos para sincronización técnica y detección temprana de desvíos.", "Sincronizaciones Diarias (Standups): ")
    add_bullet("Bitácora centralizada de defectos clasificados por severidad (Bloqueante, Crítica, Media, Leve) con verificación de pruebas de no regresión.", "Gestor de Defectos (Issue Tracking): ")
    add_bullet("Aprobación formal obligatoria para cualquier alteración a la línea base de requerimientos aprobados originalmente.", "Comité de Control de Cambios (CCB): ")
    add_bullet("Registro estructurado de eventos en 'logs/farmacia_vannesa.log' con rotación automática (RotatingFileHandler de 5 MB) y formato ISO 8601.", "Telemetría y Logging Estructurado: ")

    add_h2("1.3. Políticas de Branching, Versionamiento y Estándares de Codificación")
    add_bullet("Ramas 'main' y 'develop' protegidas. Prohibido el commit directo; se requiere Pull Request (PR) con revisión de pares.", "Protección de Ramas: ")
    add_bullet("Todo PR debe aprobar el 100% de la suite de pruebas Pytest, mantener cobertura >= 80% y pasar linters PEP 8 sin advertencias bloqueantes.", "Definition of Done (DoD): ")
    add_bullet("Adopción obligatoria de PEP 8 para el backend en Python, validado mediante Flake8 y escaneo SAST con Bandit.", "Estándar de Codificación: ")

    # ==========================================
    # 2. OBJETIVOS DE LA AUDITORÍA DE CALIDAD
    # ==========================================
    add_h1("2. Objetivos de la Auditoría de Calidad")
    add_p("Evaluar de manera objetiva, sistemática y rigurosa la efectividad, seguridad, calidad y alineación de los controles de TI en el Sistema Web de Farmacia Vannesa, garantizando la confidencialidad, integridad y disponibilidad de la información farmacéutica y transaccional, así como el cumplimiento de los estándares de calidad en cada una de las 5 fases del ciclo de vida del software.", bold_prefix="Objetivo General: ")
    
    add_p("A continuación se detallan los objetivos específicos organizados por cada fase evaluada:", bold_prefix="Objetivos Específicos: ")
    add_bullet("Validar que los requerimientos funcionales sean atómicos, estén libres de ambigüedad, cuenten con criterios de aceptación medibles y cumplan con el estándar IEEE 830.", "1. Fase Requerimientos: ")
    add_bullet("Auditar la arquitectura del software (Clean Architecture), la integridad del modelo de datos con los 11 campos mandatorios de productos y el cumplimiento de la 3FN.", "2. Fase Diseño: ")
    add_bullet("Inspeccionar la calidad intrínseca del código fuente Python, el cumplimiento de PEP 8, la seguridad estática (OWASP Top 10) y la ausencia de secretos hardcodeados.", "3. Fase Construcción: ")
    add_bullet("Comprobar la efectividad de la suite de pruebas unitarias (cobertura >= 80% en lógica de negocio), las pruebas de integración transaccional y el análisis de valores límite.", "4. Fase Pruebas (Test): ")
    add_bullet("Verificar la confiabilidad del proceso de entrega, la existencia de endpoints de monitoreo (/health con respuesta < 2s) y planes de rollback probados (RTO < 15 min).", "5. Fase Despliegue: ")

    # ==========================================
    # 3. ALCANCE Y EXCLUSIONES
    # ==========================================
    add_h1("3. Alcance y Exclusiones de la Auditoría")
    add_p("Cubre el 100% de los procesos, artefactos y herramientas del ciclo de vida del software del Sistema Web de Farmacia Vannesa (Python/Flask, Supabase PostgreSQL / SQLite local resiliente), abarcando especificaciones de requerimientos (SRS), modelos relacionales, base de código fuente, suites de pruebas automatizadas Pytest, scripts de respaldo/rollback y configuración de despliegue.", bold_prefix="Alcance: ")
    add_p("En estricto apego al requerimiento de enfocar la auditoría exclusivamente en CALIDAD DEL SISTEMA Y GOBERNANZA DEL DESARROLLO, quedan formalmente excluidos:", bold_prefix="Exclusiones Explícitas: ")
    add_bullet("Inspección de servidores físicos on-premise, racks, cableado estructurado UTP y sistemas UPS físicos de centros de cómputo.", "Hardware Físico: ")
    add_bullet("Auditoría de conmutadores (switches), enrutadores (routers), enlaces WAN y segmentación física de redes Wi-Fi de visitas.", "Redes Físicas y Telecomunicaciones: ")
    add_bullet("Auditoría contable y financiera de los balances patrimoniales de Farmacia Vannesa ajenos al software.", "Auditoría Financiera Externa: ")

    # ==========================================
    # 4. CRITERIOS Y MARCOS DE REFERENCIA
    # ==========================================
    add_h1("4. Criterios y Marcos de Referencia")
    add_p("La evaluación se fundamenta en los siguientes estándares internacionales de la industria:")
    
    crit_table = doc.add_table(rows=6, cols=3)
    crit_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(crit_table)
    
    ch = ["Estándar / Marco", "Ámbito de Aplicación", "Criterios Clave Evaluados"]
    for j, h in enumerate(ch):
        cell = crit_table.rows[0].cells[j]
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, 100, 100, 120, 120)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9)

    c_rows = [
        ("ISO 19011:2018", "Metodología de Auditoría", "Principios de auditoría, enfoque basado en riesgos, evidencia técnica verificable y papeles de trabajo formales."),
        ("ISO/IEC 25010:2011", "Calidad del Producto Software", "Adecuación funcional, fiabilidad, mantenibilidad, modularidad, usabilidad y seguridad de la aplicación."),
        ("IEEE 830:1998 / ISO 29148", "Ingeniería de Requerimientos", "Checklist de 8 características: Correcto, No ambiguo, Completo, Consistente, Clasificado, Verificable, Modificable y Trazable."),
        ("CMMI-DEV v2.0", "Madurez de Procesos SDLC", "Áreas: Planificación, Calidad de Proceso y Producto (PPQA), Verificación (VER) y Validación (VAL)."),
        ("OWASP Top 10 & PEP 8", "Construcción y Seguridad", "Mitigación de Inyección SQL, XSS, autenticación rota, exposición de secretos y guía de estilo Python.")
    ]

    for i, row_data in enumerate(c_rows, start=1):
        row = crit_table.rows[i]
        bg = ALT_ROW_HEX if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 80, 80, 100, 100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if j == 0:
                r.bold = True
                r.font.color.rgb = NAVY_RGB

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ==========================================
    # 5. CRONOGRAMA, EQUIPO AUDITOR Y RECURSOS
    # ==========================================
    add_h1("5. Equipo Auditor, Cronograma y Recursos")
    add_p("La auditoría se ejecuta durante un período de 6 semanas estructurado en 4 fases metodológicas:")

    crono_table = doc.add_table(rows=5, cols=4)
    crono_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(crono_table)
    
    cr_h = ["Fase Metodológica", "Duración", "Actividades Principales", "Entregables"]
    for j, h in enumerate(cr_h):
        cell = crono_table.rows[0].cells[j]
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, 100, 100, 120, 120)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9)

    crono_data = [
        ("Fase 1: Planificación y Contacto", "Semanas 1 y 2", "Reunión de apertura, revisión de documentación preliminar y definición de la muestra de requerimientos.", "Plan de Auditoría Aprobado y Cronograma Oficial."),
        ("Fase 2: Ejecución y Pruebas", "Semanas 3 y 4", "Aplicación de las 25 auditorías en las 5 fases del SDLC, pruebas de cobertura Pytest, escaneos SAST y verificación de rollback.", "Papeles de Trabajo y Matriz de Hallazgos Preliminares."),
        ("Fase 3: Análisis y Redacción", "Semana 5", "Consolidación de evidencias, calificación de No Conformidades y redacción del borrador del informe.", "Borrador de Informe de Auditoría y Ronda de Descargos."),
        ("Fase 4: Cierre y Resultados", "Semana 6", "Reunión formal de cierre, integración del Plan de Acción Correctiva (CAPA) y dictamen técnico final.", "Informe Final de Auditoría y Dictamen Oficial.")
    ]

    for i, row_data in enumerate(crono_data, start=1):
        row = crono_table.rows[i]
        bg = ALT_ROW_HEX if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 80, 80, 100, 100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if j == 0:
                r.bold = True
                r.font.color.rgb = NAVY_RGB

    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    add_p("Equipo Auditor Especialista: Auditor Líder SQA, Auditor de Requerimientos y Diseño, Auditor de Código y Seguridad SAST, Auditor de Testing Pytest, Auditor DevOps.<br/>Contrapartes Técnicas del Proyecto: Marvin Castañeda, Claudio Arana, Edwin Sevilla, Jester Mendieta.", bold_prefix="Personal Asignado: ")

    # ==========================================
    # 6. MATRIZ DE EVALUACIÓN DE RIESGOS DE CALIDAD
    # ==========================================
    add_h1("6. Matriz de Evaluación de Riesgos de Calidad (Metodología 1 a 3)")
    add_p("La metodología cuantitativa evalúa Probabilidad (P: 1 a 3) e Impacto (I: 1 a 3): Nivel de Severidad = P × I. Se clasifica en: 1 - 2 (Bajo / Verde), 3 - 4 (Medio / Amarillo), 6 - 9 (Alto / Rojo).")

    risk_table = doc.add_table(rows=6, cols=8)
    risk_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(risk_table)
    
    r_headers = ["ID", "Descripción del Riesgo de Calidad", "P", "I", "Riesgo Inh.", "Controles Existentes", "Riesgo Res.", "Plan de Acción / Estrategia"]
    for j, h in enumerate(r_headers):
        cell = risk_table.rows[0].cells[j]
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, 100, 100, 90, 90)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(8)

    risk_data = [
        ("R-CAL-01", "Ambigüedad o falta de atomicidad en requerimientos genera discrepancias en stock e inventario.", "3", "3", "9 (Alto)", "Revisiones manuales informales entre desarrolladores.", "2 × 2 = 4 (Medio)", "Mitigar: Implementar checklist IEEE 830 y descomposición atómica."),
        ("R-CAL-02", "Acoplamiento de lógica en Flask impide pruebas aisladas y degradación arquitectónica.", "3", "2", "6 (Alto)", "Uso parcial de repositorios y controladores.", "2 × 1 = 2 (Bajo)", "Mitigar: Consolidar Clean Architecture e inyección de dependencias."),
        ("R-CAL-03", "Deuda técnica y no apego a PEP 8 incrementa fallos latentes y costos de mantenimiento.", "2", "2", "4 (Medio)", "Revisión visual ocasional en commits.", "1 × 2 = 2 (Bajo)", "Mitigar: Validar con Flake8 y escaneo SAST Bandit en pre-commit."),
        ("R-CAL-04", "Cobertura deficiente de pruebas en transacciones de venta provoca quiebres de inventario.", "3", "3", "9 (Alto)", "Testing manual básico en el navegador.", "1 × 2 = 2 (Bajo)", "Mitigar: Suite automatizada en Pytest >= 80% y pruebas de límites."),
        ("R-CAL-05", "Despliegues manuales y fallas en migraciones provocan corrupción o caída del servicio.", "2", "3", "6 (Alto)", "Respaldo manual previo no estandarizado.", "1 × 2 = 2 (Bajo)", "Mitigar: Script 'backup_db.py' con rollback verificado en < 15 min.")
    ]

    for i, row_data in enumerate(risk_data, start=1):
        row = risk_table.rows[i]
        bg = ALT_ROW_HEX if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 90, 90)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(7.5)
            if j == 0:
                r.bold = True
                r.font.color.rgb = NAVY_RGB
            elif j in [4, 6]:
                r.bold = True
                if "9" in val or "6" in val:
                    r.font.color.rgb = RGBColor(0xC0, 0x39, 0x2B)
                elif "4" in val:
                    r.font.color.rgb = RGBColor(0xD3, 0x54, 0x00)
                else:
                    r.font.color.rgb = RGBColor(0x27, 0xAE, 0x60)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # =========================================================================
    # 7. PROGRAMA DE TRABAJO DETALLADO (25 AUDITORÍAS EN 2 PASOS OPERATIVOS)
    # =========================================================================
    add_h1("7. Programa de Trabajo de Auditoría Detallado (25 Auditorías)")
    add_p("A continuación se especifican las 25 auditorías del programa de trabajo organizadas en las 5 fases del ciclo de vida del software (SDLC). Cada auditoría se ejecuta bajo un procedimiento estructurado en dos pasos operativos:")

    def render_audit_box(code, name, ref_risk, objective, step1, step2, standard, evidence, accept_criteria):
        add_h3(f"Auditoría {code}: {name} (Ref: {ref_risk})")
        
        tbl = doc.add_table(rows=5, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl, color="CBD5E1", sz="4")
        
        info = [
            ("Objetivo de Calidad:", objective),
            ("Paso 1: Análisis Técnico y Ejecución:", step1),
            ("Paso 2: Verificación de Evidencia y Registro:", step2),
            ("Criterio de Aceptación Cuantitativo:", accept_criteria),
            ("Evidencia Esperada / Papel de Trabajo:", f"{evidence} | Estándar: {standard}")
        ]
        
        col_w = [Inches(2.2), Inches(4.8)]
        for idx, (lbl, val) in enumerate(info):
            r = tbl.rows[idx]
            c0, c1 = r.cells[0], r.cells[1]
            c0.width, c1.width = col_w[0], col_w[1]
            set_cell_background(c0, LIGHT_BG_HEX)
            set_cell_margins(c0, 70, 70, 110, 110)
            set_cell_margins(c1, 70, 70, 110, 110)
            
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
            
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ----------------------------------------------------
    # MÓDULO 1: REQUERIMIENTOS (A-01 a A-05)
    # ----------------------------------------------------
    add_h2("Módulo 1: Fase de Análisis de Requerimientos (5 Auditorías)")
    add_p("Objetivo del Módulo: Verificar que los requerimientos funcionales del sistema sean atómicos, comprensibles, verificables y cumplan con los estándares IEEE 830 e ISO/IEC 25010.")

    # Muestreo atómico de los 5 RFs
    add_p("Como parte de la ejecución de A-01 y A-02, se realiza el análisis atómico de una muestra de 5 requerimientos clave de Farmacia Vannesa:", bold_prefix="Muestreo y Análisis Atómico de Requerimientos (Muestra de 5 RFs): ")
    
    rf_table = doc.add_table(rows=6, cols=5)
    rf_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(rf_table)
    
    rf_headers = ["Requerimiento Muestreado", "Descripción Original", "Evaluación de Atomicidad", "No Ambigüedad y Testabilidad", "Dictamen y Ajuste Requerido"]
    for j, h in enumerate(rf_headers):
        cell = rf_table.rows[0].cells[j]
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, 90, 90, 90, 90)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(8)

    rf_data = [
        ("RF01: Autenticación y Control de Accesos",
         "Inicio de sesión seguro mediante usuario y contraseña encriptada, asignando roles (Admin, Farmacéutico, Vendedor) y restringiendo accesos.",
         "Parcialmente Atómico. Agrupa la autenticación (login), el almacenamiento seguro (hashing) y la autorización RBAC en un solo texto.",
         "Alta testabilidad, pero ambigua en políticas de bloqueo por reintentos fallidos y tiempo de expiración.",
         "Dividir en: RF01.1 (Autenticación), RF01.2 (Hashing seguro bcrypt/pbkdf2), RF01.3 (Control RBAC)."),
        ("RF03: Catalogación con 11 Campos",
         "Registrar medicamentos con código de barra, nombre comercial, genérico, descripción, stock, presentación, laboratorio, vencimiento, dosis, costo y venta.",
         "No Atómico (Complejo). Mezcla la gestión del catálogo maestro de productos con el control de inventario físico y lotes.",
         "Ambigüedad en validación de lotes duplicados y manejo de medicamentos controlados bajo receta médica.",
         "Desacoplar en: RF03.1 (Catálogo maestro de 11 campos) y RF03.2 (Control de existencias físicas por lote)."),
        ("RF06: Módulo de Ventas y Bloqueo",
         "Procesar ventas permitiendo agregar productos al carrito, calcular subtotales e impuestos, y bloquear transacciones si exceden el stock.",
         "No Atómico. Une cálculo comercial financiero con la regla crítica de bloqueo concurrente de inventario.",
         "Muy alta criticidad. Requiere precisión sobre concurrencia cuando dos cajeros venden la última unidad simultáneamente.",
         "Separar en: RF06.1 (Cálculo de venta y comprobante) y RF06.2 (Validación atómica y reserva concurrente de stock)."),
        ("RF09: Gestión de Inventario y Kardex",
         "Mantener actualizado el inventario en tiempo real, registrando compras, ventas, mermas y ajustes manuales en el kardex.",
         "Parcialmente Atómico. Agrupa movimientos automáticos de venta con ajustes manuales que requieren autorización de Admin.",
         "Ambigüedad en quién tiene permisos para autorizar una merma o ajuste por rotura de empaque.",
         "Separar en: RF09.1 (Kardex transaccional automático) y RF09.2 (Ajustes manuales autorizados por Admin)."),
        ("RF12: Alertas de Stock Crítico",
         "Emitir alertas en panel cuando un medicamento tenga menos de 10 unidades o venza en 30 días.",
         "No Atómico y Rígido. Agrupa dos condiciones disjuntas con umbrales fijos en lugar de ser dinámicos por producto.",
         "Rígido (umbral de 10 unidades fijo para todos los medicamentos independientemente de su rotación).",
         "Ajustar a umbrales dinámicos: RF12.1 (Alerta stock < stock_minimo) y RF12.2 (Alerta por caducidad próxima).")
    ]

    for i, row_data in enumerate(rf_data, start=1):
        row = rf_table.rows[i]
        bg = ALT_ROW_HEX if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 90, 90)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(7.5)
            if j == 0:
                r.bold = True
                r.font.color.rgb = NAVY_RGB

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    render_audit_box(
        "A-01", "Revisión de Atomicidad de Requerimientos", "R-CAL-01",
        "Verificar que cada requerimiento funcional describa una única funcionalidad independiente (principio de atomicidad).",
        "Seleccionar aleatoriamente 5 requerimientos de la especificación SRS. Analizar cada enunciado para confirmar que no contenga conjunciones copulativas ('y', 'además') que mezclen responsabilidades operativas disjuntas.",
        "Documentar la matriz de atomicidad con la justificación individual y propuesta de descomposición.",
        "ISO/IEC/IEEE 29148:2018 (Cláusula 5.2.5)", "Matriz de evaluación de atomicidad",
        "100% de los requerimientos auditados debe describir una única necesidad funcional comprobable."
    )

    render_audit_box(
        "A-02", "Revisión de Claridad y Definición", "R-CAL-01",
        "Verificar que los requerimientos sean comprensibles, técnicos y carezcan de ambigüedades o subjetividades.",
        "Inspeccionar los requerimientos en busca de términos vagos o no medibles ('rápido', 'adecuado', 'fácil'). Confirmar redacción técnica adecuada al contexto farmacéutico.",
        "Elaborar informe técnico con observaciones semánticas y recomendaciones de precisión.",
        "IEEE 830:1998 (No Ambigüedad)", "Matriz de evaluación de claridad léxica",
        "100% de los requerimientos debe poseer una única interpretación medible."
    )

    render_audit_box(
        "A-03", "Revisión de Verificabilidad y Criterios de Aceptación", "R-CAL-01",
        "Verificar que cada requerimiento cuente con criterios de aceptación medibles y pueda validarse mediante al menos un caso de prueba.",
        "Evaluar la testabilidad de cada requerimiento funcional frente a casos de prueba en Pytest. Comprobar que existan condiciones de éxito y fallo explícitas.",
        "Generar la ficha de verificabilidad vinculando el requerimiento con su correspondiente aserción automatizada.",
        "IEEE 830:1998 (Verificabilidad)", "Ficha técnica de verificabilidad y aserciones",
        "100% de los requerimientos debe ser verificable mediante pruebas computables."
    )

    render_audit_box(
        "A-04", "Revisión de Trazabilidad Bidireccional", "R-CAL-01",
        "Verificar la correspondencia bidireccional entre requerimientos, módulos de código y casos de prueba automatizados.",
        "Revisar la matriz RTM completa. Verificar que cada requerimiento tenga asociado un caso de uso, repositorio y test, detectando requerimientos huérfanos o código no especificado.",
        "Documentar la matriz RTM consolidada y el porcentaje de cobertura de trazabilidad alcanzado.",
        "CMMI-DEV v2.0 (REQM - Trazabilidad)", "Matriz de Trazabilidad Bidireccional (RTM)",
        "0% de requerimientos huérfanos y cobertura de trazabilidad >= 95%."
    )

    render_audit_box(
        "A-05", "Revisión de Cumplimiento de Normas IEEE 830", "R-CAL-01",
        "Evaluar la especificación formal frente a las 8 características mandatorias de calidad del estándar IEEE 830.",
        "Aplicar el checklist IEEE 830 evaluando si el SRS es: Correcto, No ambiguo, Completo, Consistente, Clasificado por importancia, Verificable, Modificable y Trazable.",
        "Emitir la lista de chequeo formal firmada con el porcentaje de conformidad obtenido.",
        "IEEE 830:1998 (Checklist de 8 características)", "Checklist IEEE 830 formal de conformidad",
        "Cumplimiento >= 90% en las 8 características del estándar IEEE 830."
    )

    # ----------------------------------------------------
    # MÓDULO 2: DISEÑO (A-06 a A-10)
    # ----------------------------------------------------
    add_h2("Módulo 2: Fase de Diseño de Software (5 Auditorías)")
    add_p("Objetivo del Módulo: Evaluar la calidad del diseño arquitectónico, el modelo de datos relacional con los 11 campos mandatorios, la seguridad y la modularidad.")

    render_audit_box(
        "A-06", "Revisión del Modelo de Datos (11 Campos y 3FN)", "R-CAL-02",
        "Verificar que la tabla de productos contenga los 11 campos mandatorios, tipos de datos correctos y normalización 3FN.",
        "Inspeccionar el script DDL de creación de tablas en 'sqlite_connection.py' y 'supabase_schema.sql'. Comprobar la existencia de los 11 campos: name, generic_name, product_code (código barra), description, stock (INT >= 0), presentation, laboratory, expiration_date (DATE), dose, cost_price (DECIMAL) y sale_price (DECIMAL).",
        "Verificar restricciones UNIQUE en product_code, triggers de cantidad positiva y Foreign Keys en ventas e inventario.",
        "Normalización Relacional 3FN / ISO/IEC 25010", "Script DDL auditado y diccionario de datos",
        "100% de los 11 campos presentes con tipos adecuados y clave única en product_code."
    )

    render_audit_box(
        "A-07", "Revisión de la Arquitectura de Seguridad", "R-CAL-03",
        "Verificar que la autenticación aplique funciones de hashing robustas y protección estricta de rutas.",
        "Revisar el servicio de autenticación en 'auth_service.py' y verificar uso de hash + salt con Werkzeug (scrypt/pbkdf2). Confirmar middleware de protección de rutas y registro de auditoría ante accesos no autorizados.",
        "Capturar la estructura de almacenamiento seguro de contraseñas y el código del decorador de autorización.",
        "OWASP ASVS / ISO/IEC 27001", "Evidencia de hashing seguro y código de decoradores",
        "100% de contraseñas almacenadas con hash robusto y 0 rutas administrativas expuestas."
    )

    render_audit_box(
        "A-08", "Revisión del Diseño de Integración (Arquitectura Dual)", "R-CAL-02",
        "Verificar que la integración dual (Supabase Cloud PostgreSQL y SQLite local resiliente) opere con transacciones atómicas.",
        "Examinar la inyección de dependencias en 'main.py' y repositorios. Verificar que ante indisponibilidad de la nube, el sistema conmute transparentemente al motor SQLite local sin perder integridad.",
        "Documentar el diagrama de flujo de conmutación resiliente y la consistencia transaccional ACID.",
        "Clean Architecture / Resiliencia BCP", "Diagrama de integración y prueba de conmutación",
        "Persistencia transparente con soporte de transacciones ACID en ambos motores."
    )

    render_audit_box(
        "A-09", "Revisión del Diseño de Interfaz de Usuario (UI/UX)", "R-CAL-01",
        "Evaluar la ergonomía cognitiva y velocidad operativa de despacho en mostrador farmacéutico (POS).",
        "Inspeccionar las plantillas HTML en 'app/presentation/templates/' (sales.html, inventory.html). Medir la cantidad de pulsaciones/clics requeridos para buscar por código de barra y totalizar una venta.",
        "Verificar alertas visuales destacadas para productos con bajo stock (< 10) y próximos a vencer.",
        "ISO 9241-11 (Ergonomía de Interacción)", "Evaluación heurística de usabilidad de pantallas POS",
        "Operación de venta ágil en mostrador con alertas visibles de stock crítico."
    )

    render_audit_box(
        "A-10", "Revisión del Diseño de Escalabilidad y Concurrencia", "R-CAL-02",
        "Verificar que el diseño arquitectónico soporte una carga mínima de 50 usuarios concurrentes sin quiebres de stock.",
        "Analizar el uso de índices de base de datos ('idx_products_code', claves foráneas) y la lógica de validación atómica previa al descuento de inventario en 'sales_service.py'.",
        "Documentar el análisis de contención y aislamiento transaccional para operaciones concurrentes.",
        "ISO/IEC 25010 (Eficiencia de Desempeño)", "Reporte de diseño de escalabilidad e índices DDL",
        "Diseño libre de bloqueos de tabla destructivos y capaz de soportar >= 50 sesiones simultáneas."
    )

    # ----------------------------------------------------
    # MÓDULO 3: CONSTRUCCIÓN (A-11 a A-15)
    # ----------------------------------------------------
    add_h2("Módulo 3: Fase de Construcción de Software (5 Auditorías)")
    add_p("Objetivo del Módulo: Verificar que el código fuente Python cumpla con los estándares de calidad, seguridad estática y buenas prácticas de ingeniería.")

    render_audit_box(
        "A-11", "Revisión de Calidad del Código y Complejidad Ciclomática", "R-CAL-03",
        "Verificar que el código esté libre de vulnerabilidades críticas y mantenga una complejidad ciclomática controlada.",
        "Ejecutar linters de análisis estático (Flake8) y métricas de complejidad con Radon sobre todo el código en 'app/'. Identificar code smells y métodos sobredimensionados.",
        "Documentar la matriz de complejidad ciclomática por módulo asegurando que ninguna función exceda un valor de 10.",
        "Complejidad de McCabe / ISO/IEC 25010", "Reporte de análisis estático y complejidad ciclomática",
        "Complejidad ciclomática < 10 en todas las funciones y 0 defectos críticos."
    )

    render_audit_box(
        "A-12", "Revisión de Cobertura de Pruebas Unitarias", "R-CAL-04",
        "Verificar que la cobertura de pruebas automatizadas en la lógica de negocio y servicios sea >= 80%.",
        "Ejecutar la suite completa con 'pytest --cov=app/application/services --cov=app/domain'. Medir el porcentaje total de líneas cubiertas en servicios de ventas, inventario, caja y clientes.",
        "Generar reporte de cobertura demostrando el cumplimiento del umbral requerido por el Definition of Done.",
        "IEEE 1008-1987 / Regla de Gobernanza DoD", "Reporte de cobertura emitido por Coverage.py (>= 80%)",
        "Cobertura de pruebas unitarias >= 80% (Verificado en proyecto: 84% de cobertura alcanzada)."
    )

    render_audit_box(
        "A-13", "Revisión de Codificación Segura (OWASP Top 10)", "R-CAL-03",
        "Verificar la mitigación de inyecciones SQL, Cross-Site Scripting (XSS), CSRF y exposición de datos.",
        "Ejecutar escaneo estático de seguridad SAST con Bandit sobre el árbol de código Python. Comprobar que todas las consultas SQL usen parámetros enlazados y que los formularios cuenten con tokens CSRF (Flask-WTF).",
        "Emitir reporte ejecutivo de hallazgos SAST categorizados por nivel de severidad.",
        "OWASP Top 10:2021 / CWE Top 25", "Reporte SAST generado con Bandit",
        "0 vulnerabilidades de inyección SQL, 0 vulnerabilidades de severidad alta."
    )

    render_audit_box(
        "A-14", "Revisión de Gestión de Dependencias y CVEs", "R-CAL-03",
        "Verificar que las librerías de terceros en 'requirements.txt' estén fijadas y libres de vulnerabilidades conocidas.",
        "Inspeccionar el inventario de dependencias y ejecutar 'pip-audit' contrastando paquetes contra la base de datos de vulnerabilidades NVD. Verificar versiones explícitamente pineadas.",
        "Documentar la lista de dependencias y registrar la ausencia de CVEs críticos.",
        "OWASP Top 10 (A06:2021) / ISO/IEC 25010", "Reporte de escaneo de dependencias pip-audit",
        "100% de dependencias fijadas y 0 vulnerabilidades críticas no mitigadas."
    )

    render_audit_box(
        "A-15", "Revisión de Estándares de Codificación PEP 8", "R-CAL-03",
        "Verificar el cumplimiento de la guía de estilo oficial de Python (PEP 8) y documentación de métodos.",
        "Ejecutar Flake8 sobre los módulos de la aplicación. Comprobar disciplina sintáctica, sangrías de 4 espacios, nombres en snake_case y presencia de docstrings en clases y servicios.",
        "Elaborar informe de densidad de defectos de estilo y verificación de legibilidad.",
        "Guía de Estilo PEP 8 Oficial", "Reporte de linter Flake8",
        "Cumplimiento >= 90% de reglas de estilo PEP 8 y documentación en funciones clave."
    )

    # ----------------------------------------------------
    # MÓDULO 4: DESPLIEGUE (A-16 a A-20)
    # ----------------------------------------------------
    add_h2("Módulo 4: Fase de Despliegue y Puesta en Producción (5 Auditorías)")
    add_p("Objetivo del Módulo: Evaluar la repetibilidad de las entregas, la seguridad en variables de entorno, los procedimientos de rollback y la telemetría.")

    render_audit_box(
        "A-16", "Revisión del Proceso de Entrega y Empaquetado", "R-CAL-05",
        "Verificar que el empaquetado del sistema sea reproducible y cuente con control de versiones formal.",
        "Inspeccionar los artefactos de compilación ('wsgi.py', 'Procfile', 'vannesa.spec'). Comprobar que el proceso de despliegue sea consistente y esté documentado para servidores WSGI (Gunicorn/Waitress).",
        "Documentar la bitácora de empaquetado y prueba de ejecución limpia en entorno independiente.",
        "CMMI-DEV v2.0 (Integración del Producto)", "Guía operativa de despliegue y archivo Procfile",
        "Proceso de despliegue 100% documentado, versionado y reproducible."
    )

    render_audit_box(
        "A-17", "Revisión del Plan de Rollback y Procedimientos de Reversión", "R-CAL-05",
        "Verificar que el plan de rollback de base de datos y software pueda ejecutarse en menos de 15 minutos (RTO < 15 min).",
        "Ejecutar el script automatizado 'backup_db.py --backup' para validar la creación de respaldos con verificación de integridad física. Probar el comando 'backup_db.py --restore' simulando una recuperación ante fallos.",
        "Registrar el tiempo cronometrado de restauración y la consistencia de los datos restaurados.",
        "ISO 22301 (Continuidad de Negocio)", "Bitácora de simulacro de rollback con 'backup_db.py'",
        "Tiempo de recuperación (RTO) < 15 minutos (Verificado en proyecto: < 10 segundos con 'backup_db.py')."
    )

    render_audit_box(
        "A-18", "Revisión de Aislamiento de Entornos de Prueba", "R-CAL-05",
        "Verificar que las pruebas y desarrollo operen en entornos estrictamente aislados de la base de datos de producción.",
        "Inspeccionar 'tests/conftest.py' y variables de entorno. Comprobar que la ejecución de pruebas unitarias genere bases de datos temporales independientes ('tempfile.mkstemp') sin tocar la base real.",
        "Documentar la prueba de aislamiento confirmando que los tests no alteran 'vannesa_db.sqlite' ni Supabase.",
        "ISO/IEC 25010 (Fiabilidad)", "Evidencia de fixtures aisladas en tests/conftest.py",
        "100% de aislamiento entre datos de pruebas y datos de producción."
    )

    render_audit_box(
        "A-19", "Revisión de Gestión de Variables de Entorno y Secretos", "R-CAL-03",
        "Verificar que el 100% de los secretos, API keys y URLs residan en variables de entorno seguras (.env).",
        "Escanear el código fuente en busca de contraseñas o claves hardcodeadas. Comprobar la existencia del archivo de plantilla '.env.example' debidamente documentado y la exclusión de '.env' y '.secret_key' en '.gitignore'.",
        "Generar reporte de auditoría de exclusión de secretos en el control de versiones Git.",
        "The Twelve-Factor App (Factor III: Configuración)", "Archivo .env.example y reporte de escaneo de secretos",
        "100% de secretos gestionados en variables de entorno y 0 credenciales expuestas en Git."
    )

    render_audit_box(
        "A-20", "Revisión de Monitoreo y Logging Estructurado", "R-CAL-05",
        "Verificar que el sistema registre eventos operativos con marcas de tiempo ISO 8601 y rotación de bitácoras.",
        "Inspeccionar la configuración del 'RotatingFileHandler' en 'main.py' y verificar la generación del archivo 'logs/farmacia_vannesa.log' (límite 5 MB, hasta 5 copias de respaldo). Verificar registro de método, ruta, código HTTP y latencia.",
        "Capturar un extracto de logs operativos con solicitudes reales y eventos de auditoría.",
        "OWASP ASVS (Capítulo 7) / ISO/IEC 25010", "Archivo de logs estructurados 'logs/farmacia_vannesa.log'",
        "Registro de eventos con nivel de severidad, IP, tiempo de respuesta y rotación activa."
    )

    # ----------------------------------------------------
    # MÓDULO 5: TEST (A-21 a A-25)
    # ----------------------------------------------------
    add_h2("Módulo 5: Fase de Test y Aseguramiento de Calidad (5 Auditorías)")
    add_p("Objetivo del Módulo: Validar que las suites de prueba cubran los requerimientos funcionales, valores límite y desempeño del sistema.")

    render_audit_box(
        "A-21", "Revisión de Cobertura de Requerimientos Funcionales", "R-CAL-04",
        "Verificar que los requerimientos funcionales críticos cuenten con pruebas automatizadas asociadas.",
        "Cruzar la matriz de trazabilidad frente a los 20 tests implementados en 'tests/'. Verificar que ventas, inventario, caja, clientes y autenticación posean aserciones específicas.",
        "Documentar el índice de cobertura de requerimientos demostrando cumplimiento >= 90%.",
        "ISO/IEC/IEEE 29119-2", "Matriz de cobertura requerimiento ↔ caso de prueba",
        "Cobertura de requerimientos funcionales críticos >= 90%."
    )

    render_audit_box(
        "A-22", "Revisión de Pruebas Críticas y Transaccionales", "R-CAL-04",
        "Verificar que el 100% de las pruebas transaccionales críticas se aprueben satisfactoriamente.",
        "Ejecutar los casos de prueba transaccionales: descuento atómico de inventario, registro en kardex y actualización de balance de caja. Comprobar que no existan defectos críticos abiertos.",
        "Documentar el reporte de ejecución de pruebas críticas con resultado 100% PASS.",
        "ISO/IEC/IEEE 29119-2", "Reporte de ejecución de pruebas críticas (100% PASS)",
        "100% de pruebas críticas aprobadas y 0 defectos bloqueantes."
    )

    render_audit_box(
        "A-23", "Revisión de Evidencia Técnica Verificable", "R-CAL-04",
        "Verificar que el 100% de las pruebas del plan cuente con evidencia técnica objetiva y reproducible.",
        "Inspeccionar las carpetas de evidencias, archivos JSON generados por '/health', logs de consola de Pytest y capturas de pantalla de la base de datos.",
        "Consolidar la carpeta de evidencias digitales archivadas con firma del auditor responsable.",
        "ISO 19011:2018 (Evidencia Objetiva)", "Dossier de evidencias digitales verificables",
        "100% de las pruebas sustentadas con evidencias técnicas trazables."
    )

    render_audit_box(
        "A-24", "Revisión de Pruebas de Regresión y Valores Límite", "R-CAL-04",
        "Verificar la existencia de una suite de regresión automatizada que evalúe casos de frontera (Boundary Testing).",
        "Ejecutar 'test_quality_and_services.py' validando: venta de la última unidad (stock = 0), intento de venta con stock insuficiente (+1), inserción de cantidades negativas y cliente duplicado.",
        "Registrar los resultados de las aserciones de valores frontera y resistencia ante entradas anómalas.",
        "ISO/IEC/IEEE 29119-4 (Boundary Value Testing)", "Suite de pruebas de regresión y valores límite",
        "Suite de regresión automatizada ejecutable en menos de 10 segundos con 100% PASS."
    )

    render_audit_box(
        "A-25", "Revisión de Pruebas de Rendimiento y Health Check", "R-CAL-05",
        "Verificar que los endpoints del sistema respondan con tiempos de latencia menores a 2.0 segundos.",
        "Realizar solicitudes de monitoreo al endpoint '/health' y medir el tiempo de respuesta. Comprobar que responda con código HTTP 200 OK y estructura JSON indicando estado 'UP' y conectividad de base de datos.",
        "Documentar las métricas de latencia registradas en las bitácoras estructuradas.",
        "ISO/IEC 25010 (Tiempo de Respuesta)", "Registro de latencia de /health en logs estructurados",
        "Tiempo de respuesta < 2.0 segundos (Verificado en proyecto: 1.1 milisegundos en /health)."
    )

    # =========================================================================
    # 8. TABLA CONSOLIDADA: PROGRAMA INTEGRAL DE 25 AUDITORÍAS
    # =========================================================================
    add_h1("8. Tabla Resumen del Programa de Trabajo (25 Auditorías)")
    add_p("A continuación se consolida la matriz operativa completa cruzando código de riesgo, fase del SDLC, auditoría, pasos, evidencia y responsable asignado:")

    full_tbl = doc.add_table(rows=26, cols=7)
    full_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(full_tbl)
    
    fh = ["Cód.", "Fase SDLC", "Auditoría", "Procedimiento Operativo", "Evidencia Principal", "Formato", "Responsable"]
    for j, h in enumerate(fh):
        cell = full_tbl.rows[0].cells[j]
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, 80, 80, 70, 70)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(7.5)

    summary_rows = [
        ("R-CAL-01", "1. Requerimientos", "A-01: Atomicidad", "Paso 1: Muestreo de 5 RFs / Paso 2: Matriz atómica.", "Matriz de evaluación atómica", "Word / PDF", "Auditor Requisitos"),
        ("R-CAL-01", "1. Requerimientos", "A-02: Claridad", "Paso 1: Análisis léxico / Paso 2: Eliminación de ambigüedades.", "Matriz de claridad léxica", "Word / PDF", "Auditor Requisitos"),
        ("R-CAL-01", "1. Requerimientos", "A-03: Verificabilidad", "Paso 1: Testabilidad / Paso 2: Ficha de aserciones.", "Ficha técnica de verificabilidad", "Excel / Word", "Auditor de QA"),
        ("R-CAL-01", "1. Requerimientos", "A-04: Trazabilidad", "Paso 1: Matriz RTM / Paso 2: Detección de huérfanos.", "Matriz RTM bidireccional", "Excel", "Auditor de QA"),
        ("R-CAL-01", "1. Requerimientos", "A-05: Norma IEEE 830", "Paso 1: Checklist 8 criterios / Paso 2: Acta de conformidad.", "Checklist IEEE 830 formal", "PDF firmado", "Auditor de QA"),
        ("R-CAL-02", "2. Diseño", "A-06: Modelo de Datos", "Paso 1: DDL 11 campos / Paso 2: Verificación de 3FN e índices.", "Script DDL y diccionario de datos", "SQL / PDF", "Auditor de Calidad"),
        ("R-CAL-03", "2. Diseño", "A-07: Arq. Seguridad", "Paso 1: Hash scrypt/pbkdf2 / Paso 2: Decoradores de ruta.", "Captura hash BD y middleware", "Código / PDF", "Auditor Seguridad"),
        ("R-CAL-02", "2. Diseño", "A-08: Integración Dual", "Paso 1: Inyección dependencias / Paso 2: Conmutación resiliente.", "Diagrama arquitectura resiliente", "UML / PDF", "Auditor de Calidad"),
        ("R-CAL-01", "2. Diseño", "A-09: Diseño UI/UX", "Paso 1: Ergonomía POS / Paso 2: Alertas visuales de stock.", "Evaluación heurística usabilidad", "PDF / Figma", "Auditor de Calidad"),
        ("R-CAL-02", "2. Diseño", "A-10: Escalabilidad", "Paso 1: Análisis concurrencia / Paso 2: Índices en BD.", "Reporte diseño concurrente", "PDF", "Auditor Infraest."),
        ("R-CAL-03", "3. Construcción", "A-11: Calidad Código", "Paso 1: Análisis estático / Paso 2: Complejidad Radon < 10.", "Reporte Flake8 y complejidad", "HTML / PDF", "Auditor de Calidad"),
        ("R-CAL-04", "3. Construcción", "A-12: Tests Unitarios", "Paso 1: Ejecución Pytest / Paso 2: Medición Coverage >= 80%.", "Reporte Coverage.py (84% alcanzado)", "HTML / PDF", "Auditor de QA"),
        ("R-CAL-03", "3. Construcción", "A-13: OWASP Top 10", "Paso 1: Escaneo Bandit SAST / Paso 2: Queries parametrizadas.", "Reporte escáner Bandit", "JSON / PDF", "Auditor Seguridad"),
        ("R-CAL-03", "3. Construcción", "A-14: Dependencias", "Paso 1: Auditoría pip-audit / Paso 2: Fijación en requirements.", "Reporte de escaneo CVE", "JSON / TXT", "Auditor Seguridad"),
        ("R-CAL-03", "3. Construcción", "A-15: Estándar PEP 8", "Paso 1: Linter Flake8 / Paso 2: Docstrings en servicios.", "Reporte de estilo PEP 8", "TXT / PDF", "Auditor de Calidad"),
        ("R-CAL-05", "4. Despliegue", "A-16: Proceso Entrega", "Paso 1: Revisión empaquetado / Paso 2: Procfile y wsgi.py.", "Guía operativa de despliegue", "PDF", "Ingeniero DevOps"),
        ("R-CAL-05", "4. Despliegue", "A-17: Plan Rollback", "Paso 1: Respaldo preventivo / Paso 2: Simulacro con backup_db.", "Log de backup_db.py (< 10s)", "Log / PDF", "Ingeniero DevOps"),
        ("R-CAL-05", "4. Despliegue", "A-18: Aislamiento", "Paso 1: Fixtures temporales / Paso 2: Protección datos prod.", "Evidencia tests/conftest.py", "Código / Log", "Ingeniero DevOps"),
        ("R-CAL-03", "4. Despliegue", "A-19: Secretos (.env)", "Paso 1: Escaneo secretos / Paso 2: Plantilla .env.example.", "Archivo .env.example y .gitignore", "Archivo config", "Auditor Seguridad"),
        ("R-CAL-05", "4. Despliegue", "A-20: Monitoreo/Logs", "Paso 1: RotatingFileHandler / Paso 2: farmacia_vannesa.log.", "Bitácora estructurada de logs", "Archivo .log", "Ingeniero DevOps"),
        ("R-CAL-04", "5. Test", "A-21: Cobertura Req.", "Paso 1: Cruce RF vs Pytest / Paso 2: Aserciones críticas.", "Matriz trazabilidad prueba-req", "Excel / PDF", "Ingeniero de QA"),
        ("R-CAL-04", "5. Test", "A-22: Pruebas Críticas", "Paso 1: Tests transaccionales / Paso 2: Validación 100% PASS.", "Reporte pruebas transaccionales", "HTML / Log", "Ingeniero de QA"),
        ("R-CAL-04", "5. Test", "A-23: Evidencia Técnica", "Paso 1: Recopilación logs / Paso 2: Dossier digital verificado.", "Carpeta de evidencias digitales", "ZIP / PDF", "Ingeniero de QA"),
        ("R-CAL-04", "5. Test", "A-24: Regresión/Límites", "Paso 1: Boundary testing / Paso 2: Stock cero y sobreventa.", "Suite test_quality_and_services", "Código / Log", "Ingeniero de QA"),
        ("R-CAL-05", "5. Test", "A-25: Rendimiento", "Paso 1: Solicitud /health / Paso 2: Latencia < 2.0s.", "Logs de latencia en /health", "JSON / Log", "Ingeniero de QA")
    ]

    for i, row_data in enumerate(summary_rows, start=1):
        row = full_tbl.rows[i]
        bg = ALT_ROW_HEX if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 70, 70)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(7)
            if j == 0:
                r.bold = True
                r.font.color.rgb = NAVY_RGB

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # =========================================================================
    # 9. CRITERIOS DE CALIFICACIÓN Y FORMALIZACIÓN
    # =========================================================================
    add_h1("9. Calificación de Hallazgos y Formalización Institucional")
    add_bullet("Incumplimiento crítico que compromete la integridad del inventario, la seguridad de contraseñas o paraliza el servicio. Requiere subsanación obligatoria previa a cualquier paso a producción.", "No Conformidad Mayor (NC Mayor): ")
    add_bullet("Desviación que no degrada críticamente la operación (estilo PEP 8 menor o cobertura ligeramente bajo el umbral). Subsanable en el ciclo regular.", "No Conformidad Menor (NC Menor): ")
    add_bullet("Aspecto que cumple los requisitos mínimos pero presenta oportunidad de optimización de modularidad o rendimiento.", "Oportunidad de Mejora (OM): ")

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    add_p("El presente Plan de Auditoría de Calidad es suscrito formalmente para su aprobación y ejecución técnica:", bold_prefix="Formalización Institucional: ")
    
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
        set_cell_margins(c_sig, 120, 120, 120, 120)
        p = c_sig.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(sig_cells[j])
        r.font.size = Pt(8.5)
        r.font.color.rgb = NAVY_RGB
        
        c_sig2 = sig_table.rows[1].cells[j]
        set_cell_background(c_sig2, "FFFFFF")
        set_cell_margins(c_sig2, 90, 90, 120, 120)
        p2 = c_sig2.paragraphs[0]
        p2.paragraph_format.space_after = Pt(0)
        r2 = p2.add_run("Fecha: Octubre 2026\nEstado: PLAN APROBADO PARA EJECUCIÓN")
        r2.font.size = Pt(8)
        r2.font.italic = True
        r2.font.color.rgb = MUTED_RGB

    output_path = r"c:\Proyectos\Farmacia-Vannesa\Plan_Auditoria_Calidad_Farmacia_Vannesa.docx"
    doc.save(output_path)
    print(f"Documento Word guardado exitosamente en: {output_path}")

if __name__ == "__main__":
    create_document()
