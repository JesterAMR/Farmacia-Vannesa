from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.application.services.auth_service import AuthService
from app.application.services.audit_service import AuditService
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def create_auth_blueprint(auth_service: AuthService, audit_service: AuditService = None) -> Blueprint:
    bp = Blueprint('auth', __name__, url_prefix='/auth')

    @bp.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            try:
                user = auth_service.login(username, password)
            except Exception as e:
                logger.error(f"[Auth Error] Fallo al autenticar: {e}")
                err_msg = str(e)
                if 'Unregistered API key' in err_msg or '401' in err_msg:
                    flash('Error de credenciales (401): Clave de API no válida.', 'error')
                else:
                    flash(f'Error al conectar con la base de datos: {e}', 'error')
                return render_template('login.html')

            if user:
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                
                if audit_service:
                    audit_service.log_action(
                        action="Inicio de sesión exitoso",
                        user_id=user.id,
                        details=f"Usuario: {user.username}, Rol: {user.role}"
                    )

                flash('Has iniciado sesión correctamente.', 'success')
                if user.role == 'admin':
                    return redirect(url_for('dashboard.index'))
                else:
                    return redirect(url_for('sales.index'))

            # Intento fallido
            if audit_service:
                audit_service.log_action(
                    action="Intento fallido de inicio de sesión",
                    user_id=None,
                    details=f"Intento con usuario: '{username}'"
                )

            flash('Usuario o contraseña incorrectos.', 'error')
        return render_template('login.html')

    @bp.route('/register', methods=['GET', 'POST'])
    def register():
        user_count = 0
        try:
            user_count = auth_service.count_users()
        except Exception as e:
            logger.warning(f"Error checking user count: {e}")

        is_bootstrap = (user_count == 0)

        # Si ya existen usuarios, solo un administrador autenticado puede registrar nuevos usuarios
        if not is_bootstrap:
            if 'user_id' not in session or session.get('role') != 'admin':
                flash('El registro de nuevos usuarios está reservado exclusivamente para el Administrador del sistema.', 'error')
                return redirect(url_for('auth.login'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            role = request.form.get('role')
            if is_bootstrap:
                role = 'admin'
            elif not role:
                role = 'cajero'

            try:
                success = auth_service.register(username, password, role=role)
            except Exception as e:
                logger.error(f"[Auth Register Error] {e}")
                flash(f'Error al registrar usuario: {e}', 'error')
                return render_template('register.html', is_bootstrap=is_bootstrap)

            if success:
                if audit_service:
                    audit_service.log_action(
                        action="Registró nuevo usuario",
                        user_id=session.get('user_id'),
                        details=f"Usuario creado: '{username}', Rol asignado: {role}"
                    )

                if is_bootstrap:
                    flash('¡Administrador inicial registrado exitosamente! Ahora puedes iniciar sesión.', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    flash(f'Usuario "{username}" ({role}) registrado exitosamente.', 'success')
                    return redirect(url_for('dashboard.index'))
            else:
                flash('El nombre de usuario ya existe.', 'error')

        return render_template('register.html', is_bootstrap=is_bootstrap)

    @bp.route('/logout')
    def logout():
        uid = session.get('user_id')
        uname = session.get('username')
        if audit_service and uid:
            audit_service.log_action(
                action="Cierre de sesión",
                user_id=uid,
                details=f"Usuario: {uname}"
            )
        session.clear()
        flash('Has cerrado sesión.', 'success')
        return redirect(url_for('auth.login'))

    return bp

# Middleware Decorator para proteger rutas de Flask
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Acceso denegado: Se requieren permisos de Administrador.', 'error')
            return redirect(url_for('sales.index'))
        return f(*args, **kwargs)
    return decorated_function
