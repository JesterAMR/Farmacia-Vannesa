from flask import Blueprint, render_template, request, session
from app.presentation.routes.auth import login_required
from app.application.services.inventory_service import InventoryService
from app.application.services.sales_service import SalesService
from collections import defaultdict
from datetime import datetime

def create_stats_blueprint(inventory_service: InventoryService, sales_service: SalesService) -> Blueprint:
    bp = Blueprint('stats', __name__, url_prefix='/stats')

    @bp.route('/top-bottom')
    @login_required
    def top_bottom_products():
        period = request.args.get('period', 'monthly')
        all_products = inventory_service.get_all_products(include_inactive=False)
        all_sales = sales_service.get_all_sales()

        # Mapear productos por ID para acceso rápido
        prod_map = {p.id: p for p in all_products}

        # Acumular unidades vendidas y recaudación por producto
        units_by_product = defaultdict(int)
        revenue_by_product = defaultdict(float)

        for sale in all_sales:
            for item in sale.items:
                units_by_product[item.product_id] += item.quantity
                revenue_by_product[item.product_id] += item.subtotal

        # Ordenar productos con ventas para el Top
        ranked_sales = sorted(
            units_by_product.items(),
            key=lambda x: x[1],
            reverse=True
        )

        max_units = ranked_sales[0][1] if ranked_sales else 1

        top_products = []
        for rank, (prod_id, units) in enumerate(ranked_sales[:10], start=1):
            p = prod_map.get(prod_id)
            if not p:
                continue
            pct = int((units / max_units) * 100) if max_units > 0 else 0
            stock_status = "Óptimo" if p.stock > 30 else ("Medio" if p.stock > 10 else "Bajo")
            badge_color = "var(--success)" if p.stock > 30 else ("var(--primary)" if p.stock > 10 else "var(--danger)")

            top_products.append({
                "rank": rank,
                "code": p.product_code or f"MED-{p.id:03d}",
                "name": p.name,
                "generic": p.generic_name or p.name,
                "laboratory": p.laboratory or "Genérico",
                "units_sold": units,
                "percentage": pct,
                "unit_price": p.sale_price,
                "revenue": round(revenue_by_product[prod_id], 2),
                "current_stock": p.stock,
                "stock_status": stock_status,
                "badge_color": badge_color
            })

        # Productos con menos ventas o sin ventas (Baja rotación / Capital estancado)
        bottom_candidates = []
        for p in all_products:
            sold = units_by_product.get(p.id, 0)
            tied_capital = round(p.stock * p.cost_price, 2)
            bottom_candidates.append({
                "product": p,
                "units_sold": sold,
                "tied_capital": tied_capital
            })

        # Ordenar por menores ventas y luego por mayor capital estancado
        bottom_candidates.sort(key=lambda x: (x["units_sold"], -x["tied_capital"]))

        bottom_products = []
        for rank, item in enumerate(bottom_candidates[:10], start=1):
            p = item["product"]
            sold = item["units_sold"]
            urgency = "Crítica" if p.stock > 20 and sold == 0 else ("Alta" if sold == 0 else "Media")
            badge_urgency = "var(--danger)" if urgency == "Crítica" else ("var(--warning)" if urgency == "Alta" else "#38bdf8")
            recom = "Promoción o Descuento" if sold == 0 else "Reubicar en exhibición"

            bottom_products.append({
                "rank": rank,
                "code": p.product_code or f"MED-{p.id:03d}",
                "name": p.name,
                "generic": p.generic_name or p.name,
                "laboratory": p.laboratory or "Genérico",
                "units_sold": sold,
                "days_without_sale": 30 if sold == 0 else 5,
                "current_stock": p.stock,
                "cost_price": p.cost_price,
                "tied_capital": item["tied_capital"],
                "expiration_date": p.expiration_date or "N/D",
                "recommendation": recom,
                "urgency": urgency,
                "badge_urgency": badge_urgency
            })

        # Métricas generales de resumen
        total_units = sum(units_by_product.values())
        total_top_revenue = sum(revenue_by_product.values())
        total_tied_capital = sum(item["tied_capital"] for item in bottom_candidates)

        top_prod_name = top_products[0]["name"] if top_products else "Ninguno aún"
        top_units_count = top_products[0]["units_sold"] if top_products else 0
        least_prod_name = bottom_products[0]["name"] if bottom_products else "Ninguno aún"
        least_units_count = bottom_products[0]["units_sold"] if bottom_products else 0

        summary = {
            "top_product": top_prod_name,
            "top_units": top_units_count,
            "least_sold_product": least_prod_name,
            "least_units": least_units_count,
            "total_top_revenue": total_top_revenue,
            "total_units_sold": total_units,
            "total_tied_capital": total_tied_capital,
            "period": period
        }

        return render_template('top_bottom_products.html',
                               top_products=top_products,
                               bottom_products=bottom_products,
                               summary=summary)

    return bp
