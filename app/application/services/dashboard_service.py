from app.application.interfaces.sale_repository import SaleRepositoryInterface
from app.application.interfaces.product_repository import ProductRepositoryInterface
import datetime

class DashboardService:
    def __init__(self, sale_repository: SaleRepositoryInterface, product_repository: ProductRepositoryInterface, audit_service = None):
        self._sale_repository = sale_repository
        self._product_repository = product_repository
        self._audit_service = audit_service

    def get_summary(self):
        sales = self._sale_repository.get_all()
        products = self._product_repository.get_all()
        
        total_revenue = sum(sale.total for sale in sales)
        total_sales = len(sales)
        low_stock_products = sum(1 for p in products if p.stock < 10)
        
        import datetime as dt_mod
        
        def parse_date(date_str: str) -> dt_mod.date:
            for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return dt_mod.datetime.strptime(date_str, fmt).date()
                except ValueError:
                    pass
            # Split by T or space
            cleaned = date_str.replace("T", " ").split(" ")[0]
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
                try:
                    return dt_mod.datetime.strptime(cleaned, fmt).date()
                except ValueError:
                    pass
            return dt_mod.date.today()

        # Collect all unique months in sales
        all_months = set()
        for sale in sales:
            parsed_sale_date = parse_date(sale.date)
            all_months.add(parsed_sale_date.strftime("%Y-%m"))

        # Current calendar month
        current_month = dt_mod.datetime.now().strftime("%Y-%m")
        
        # If no sales in current calendar month, fallback to latest month in DB
        if sales and current_month not in all_months and all_months:
            current_month = max(all_months)
        
        # Calculate inventory valuation
        total_items = sum(p.stock for p in products)
        total_cost_value = sum(p.stock * p.cost_price for p in products)
        total_sale_value = sum(p.stock * p.sale_price for p in products)
        
        # Calculate daily sales for chart
        daily_sales = {}
        monthly_sales_revenue = 0.0
        product_sales_current_month = {}
        product_sales = {}
        
        for sale in sales:
            parsed_date = parse_date(sale.date)
            date_only = parsed_date.strftime("%Y-%m-%d")
            month_only = parsed_date.strftime("%Y-%m")
            
            daily_sales.setdefault(date_only, 0.0)
            daily_sales[date_only] += sale.total
            
            if month_only == current_month:
                monthly_sales_revenue += sale.total
            
            for item in sale.items:
                product_sales.setdefault(item.product_id, 0)
                product_sales[item.product_id] += item.quantity
                
                if month_only == current_month:
                    product_sales_current_month.setdefault(item.product_id, 0)
                    product_sales_current_month[item.product_id] += item.quantity
                
        # Get product names
        top_products = []
        for pid, qty in sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]:
            product = self._product_repository.get_by_id(pid)
            if product:
                top_products.append({"name": product.name, "quantity": qty})
                
        # Least sold product current month (with at least 1 sale)
        least_sold_product = {"name": "Ninguno", "quantity": 0}
        if product_sales_current_month:
            least_pid = min(product_sales_current_month, key=product_sales_current_month.get)
            min_qty = product_sales_current_month[least_pid]
            product = self._product_repository.get_by_id(least_pid)
            if product:
                least_sold_product = {"name": product.name, "quantity": min_qty}
                
        # Sort daily sales by date key (YYYY-MM-DD) chronologically
        sorted_daily_sales = dict(sorted(daily_sales.items())[-7:])

        # Calculate expiring or expired products (within 90 days)
        expiring_products = []
        today = dt_mod.date.today()
        ninety_days_from_now = today + dt_mod.timedelta(days=90)
        
        for p in products:
            if p.expiration_date:
                try:
                    exp_date = parse_date(p.expiration_date)
                    if exp_date <= today:
                        expiring_products.append({
                            "id": p.id,
                            "name": p.name,
                            "code": p.product_code,
                            "status": "Vencido",
                            "date": p.expiration_date
                        })
                    elif exp_date <= ninety_days_from_now:
                        expiring_products.append({
                            "id": p.id,
                            "name": p.name,
                            "code": p.product_code,
                            "status": "Próximo a vencer",
                            "date": p.expiration_date
                        })
                except Exception:
                    pass

        # Get recent audit logs
        recent_logs = self._audit_service.get_recent_logs(10) if self._audit_service else []

        return {
            "total_revenue": total_revenue,
            "total_sales": total_sales,
            "low_stock_count": low_stock_products,
            "daily_sales": sorted_daily_sales,
            "top_products": top_products,
            "least_sold_product": least_sold_product,
            "monthly_sales_revenue": monthly_sales_revenue,
            "total_items": total_items,
            "total_cost_value": total_cost_value,
            "total_sale_value": total_sale_value,
            "expiring_products": expiring_products,
            "recent_logs": recent_logs
        }
