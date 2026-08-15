from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.application.services.client_service import ClientService
from app.presentation.routes.auth import login_required, admin_required
from app.application.services.audit_service import AuditService
from flask import session

def create_client_blueprint(client_service: ClientService, audit_service: AuditService) -> Blueprint:
    bp = Blueprint('client', __name__, url_prefix='/clients')

    @bp.route('/')
    @login_required
    def index():
        clients = client_service.get_all_clients()
        return render_template('clients.html', clients=clients)

    @bp.route('/add', methods=['POST'])
    @login_required
    def add():
        name = request.form.get('name')
        identity_card = request.form.get('identity_card')
        email = request.form.get('email') or None
        phone = request.form.get('phone') or None
        
        try:
            client = client_service.create_client(name, identity_card, email, phone)
            audit_service.log_action(
                action=f"Registró cliente: {client.name}",
                user_id=session.get('user_id'),
                details=f"ID: {client.id}, Cédula: {client.identity_card}"
            )
            flash("Cliente registrado exitosamente.", "success")
        except ValueError as e:
            flash(str(e), "error")
        return redirect(url_for('client.index'))

    @bp.route('/update/<int:id>', methods=['POST'])
    @login_required
    def update(id: int):
        name = request.form.get('name')
        identity_card = request.form.get('identity_card')
        email = request.form.get('email') or None
        phone = request.form.get('phone') or None
        
        try:
            client = client_service.update_client(id, name, identity_card, email, phone)
            audit_service.log_action(
                action=f"Actualizó cliente: {client.name}",
                user_id=session.get('user_id'),
                details=f"ID: {client.id}, Cédula: {client.identity_card}"
            )
            flash("Cliente actualizado exitosamente.", "success")
        except ValueError as e:
            flash(str(e), "error")
        return redirect(url_for('client.index'))

    @bp.route('/delete/<int:id>', methods=['POST'])
    @login_required
    @admin_required
    def delete(id: int):
        client = client_service.get_client(id)
        if client:
            client_service.delete_client(id)
            audit_service.log_action(
                action=f"Eliminó cliente: {client.name}",
                user_id=session.get('user_id'),
                details=f"ID: {client.id}, Cédula: {client.identity_card}"
            )
            flash("Cliente eliminado correctamente.", "success")
        else:
            flash("Cliente no encontrado.", "error")
        return redirect(url_for('client.index'))

    @bp.route('/api/search')
    @login_required
    def api_search():
        identity = request.args.get('identity_card', '')
        client = client_service.get_client_by_identity(identity)
        if client:
            return jsonify({
                "found": True,
                "id": client.id,
                "name": client.name,
                "identity_card": client.identity_card
            })
        return jsonify({"found": False})

    return bp
