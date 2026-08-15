from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.application.services.auth_service import AuthService
from functools import wraps

def create_auth_blueprint(auth_service: AuthService) -> Blueprint:
    bp = Blueprint('auth', __name__, url_prefix='/auth')

    @bp.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = auth_service.login(username, password)
            if user:
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                flash('Has iniciado sesión correctamente.', 'success')
                if user.role == 'admin':
                    return redirect(url_for('dashboard.index'))
                else:
                    return redirect(url_for('sales.index'))
            flash('Usuario o contraseña incorrectos.', 'error')
        return render_template('login.html')

    @bp.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if auth_service.register(username, password):
                flash('Usuario registrado exitosamente. Ahora puedes iniciar sesión.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('El nombre de usuario ya existe.', 'error')
        return render_template('register.html')

    @bp.route('/logout')
    def logout():
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
            # Redirect cashiers to the sales dashboard instead of the admin dashboard
            return redirect(url_for('sales.index'))
        return f(*args, **kwargs)
    return decorated_function
