from flask import Blueprint, render_template
from app.application.services.dashboard_service import DashboardService
from app.presentation.routes.auth import login_required, admin_required

def create_dashboard_blueprint(dashboard_service: DashboardService) -> Blueprint:
    bp = Blueprint('dashboard', __name__)

    @bp.route('/')
    @login_required
    @admin_required
    def index():
        summary = dashboard_service.get_summary()
        return render_template('dashboard.html', summary=summary)

    @bp.route('/cutoff')
    @login_required
    @admin_required
    def monthly_cutoff():
        summary = dashboard_service.get_summary()
        return render_template('cutoff.html', summary=summary)

    @bp.route('/api/summary')
    @login_required
    @admin_required
    def api_summary():
        from flask import request, jsonify
        range_type = request.args.get('range_type', '7days')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        summary = dashboard_service.get_summary_for_range(range_type, start_date, end_date)
        return jsonify(summary)

    return bp
