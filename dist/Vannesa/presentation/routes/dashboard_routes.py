from flask import Blueprint, render_template
from app.application.services.dashboard_service import DashboardService
from app.presentation.routes.auth import login_required

def create_dashboard_blueprint(dashboard_service: DashboardService) -> Blueprint:
    bp = Blueprint('dashboard', __name__)

    @bp.route('/')
    @login_required
    def index():
        summary = dashboard_service.get_summary()
        return render_template('dashboard.html', summary=summary)

    @bp.route('/cutoff')
    @login_required
    def monthly_cutoff():
        summary = dashboard_service.get_summary()
        return render_template('cutoff.html', summary=summary)

    return bp
