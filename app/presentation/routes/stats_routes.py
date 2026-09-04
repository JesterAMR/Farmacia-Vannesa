from flask import Blueprint, render_template, request, session
from app.presentation.routes.auth import login_required

def create_stats_blueprint() -> Blueprint:
    bp = Blueprint('stats', __name__, url_prefix='/stats')

    @bp.route('/top-bottom')
    @login_required
    def top_bottom_products():
        period = request.args.get('period', 'monthly')

        # Mock data visual para productos más vendidos (Top Sellers)
        top_products = [
            {
                "rank": 1,
                "code": "MED-001",
                "name": "Paracetamol 500mg",
                "generic": "Acetaminofén",
                "laboratory": "Ramos",
                "units_sold": 184,
                "percentage": 100,
                "unit_price": 15.00,
                "revenue": 2760.00,
                "current_stock": 150,
                "stock_status": "Óptimo",
                "badge_color": "var(--success)"
            },
            {
                "rank": 2,
                "code": "MED-004",
                "name": "Ibuprofeno 400mg",
                "generic": "Ibuprofeno",
                "laboratory": "MK",
                "units_sold": 142,
                "percentage": 77,
                "unit_price": 20.00,
                "revenue": 2840.00,
                "current_stock": 33,
                "stock_status": "Medio",
                "badge_color": "var(--primary)"
            },
            {
                "rank": 3,
                "code": "MED-002",
                "name": "Amoxicilina 500mg",
                "generic": "Amoxicilina Trihidrato",
                "laboratory": "Calox",
                "units_sold": 115,
                "percentage": 62,
                "unit_price": 35.00,
                "revenue": 4025.00,
                "current_stock": 23,
                "stock_status": "Normal",
                "badge_color": "var(--primary)"
            },
            {
                "rank": 4,
                "code": "MED-005",
                "name": "Loratadina 10mg",
                "generic": "Loratadina",
                "laboratory": "Ramos",
                "units_sold": 98,
                "percentage": 53,
                "unit_price": 12.00,
                "revenue": 1176.00,
                "current_stock": 14,
                "stock_status": "Normal",
                "badge_color": "var(--primary)"
            },
            {
                "rank": 5,
                "code": "MED-008",
                "name": "Omeprazol 20mg",
                "generic": "Omeprazol",
                "laboratory": "MK",
                "units_sold": 87,
                "percentage": 47,
                "unit_price": 25.00,
                "revenue": 2175.00,
                "current_stock": 62,
                "stock_status": "Óptimo",
                "badge_color": "var(--primary)"
            },
            {
                "rank": 6,
                "code": "MED-015",
                "name": "Acetaminofén Jarabe 120ml",
                "generic": "Acetaminofén",
                "laboratory": "Infasa",
                "units_sold": 64,
                "percentage": 35,
                "unit_price": 45.00,
                "revenue": 2880.00,
                "current_stock": 27,
                "stock_status": "Normal",
                "badge_color": "var(--primary)"
            }
        ]

        # Mock data visual para productos menos vendidos (Baja rotación / Estancados)
        bottom_products = [
            {
                "rank": 1,
                "code": "MED-042",
                "name": "Espironolactona 25mg",
                "generic": "Espironolactona",
                "laboratory": "Menarini",
                "units_sold": 0,
                "days_without_sale": 75,
                "current_stock": 18,
                "cost_price": 65.00,
                "tied_capital": 1170.00,
                "expiration_date": "2026-11-15",
                "recommendation": "Descuento 20% / Promoción",
                "urgency": "Alta",
                "badge_urgency": "var(--danger)"
            },
            {
                "rank": 2,
                "code": "MED-039",
                "name": "Metildopa 250mg",
                "generic": "Metildopa",
                "laboratory": "Bayer",
                "units_sold": 1,
                "days_without_sale": 58,
                "current_stock": 24,
                "cost_price": 48.00,
                "tied_capital": 1152.00,
                "expiration_date": "2026-12-30",
                "recommendation": "Reubicar en exhibición",
                "urgency": "Media",
                "badge_urgency": "var(--warning)"
            },
            {
                "rank": 3,
                "code": "MED-055",
                "name": "Ketoconazol Crema 2% 30g",
                "generic": "Ketoconazol",
                "laboratory": "Medinfar",
                "units_sold": 1,
                "days_without_sale": 52,
                "current_stock": 12,
                "cost_price": 55.00,
                "tied_capital": 660.00,
                "expiration_date": "2027-02-10",
                "recommendation": "Consultar rotación con médico",
                "urgency": "Baja",
                "badge_urgency": "#38bdf8"
            },
            {
                "rank": 4,
                "code": "MED-061",
                "name": "Ranitidina 150mg",
                "generic": "Ranitidina Clorhidrato",
                "laboratory": "MK",
                "units_sold": 2,
                "days_without_sale": 44,
                "current_stock": 30,
                "cost_price": 18.00,
                "tied_capital": 540.00,
                "expiration_date": "2027-01-20",
                "recommendation": "Sustituir por Omeprazol",
                "urgency": "Media",
                "badge_urgency": "var(--warning)"
            },
            {
                "rank": 5,
                "code": "MED-070",
                "name": "Dexametasona Ampolla 4mg/2ml",
                "generic": "Dexametasona Fosfato",
                "laboratory": "Pharmalat",
                "units_sold": 2,
                "days_without_sale": 39,
                "current_stock": 15,
                "cost_price": 32.00,
                "tied_capital": 480.00,
                "expiration_date": "2026-10-05",
                "recommendation": "Próximo a vencer / Descuento",
                "urgency": "Crítica",
                "badge_urgency": "var(--danger)"
            }
        ]

        # Resumen de KPIs
        summary = {
            "top_product": "Paracetamol 500mg",
            "top_units": 184,
            "least_sold_product": "Espironolactona 25mg",
            "least_units": 0,
            "total_top_revenue": 15856.00,
            "total_units_sold": 690,
            "total_tied_capital": 4002.00,
            "period": period
        }

        return render_template('top_bottom_products.html',
                               top_products=top_products,
                               bottom_products=bottom_products,
                               summary=summary)

    return bp
