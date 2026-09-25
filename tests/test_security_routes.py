def test_protected_routes_redirect_anonymous(client):
    # Intentar acceder al dashboard sin sesión debe redirigir a login
    res = client.get('/', follow_redirects=False)
    assert res.status_code in (301, 302)
    assert '/auth/login' in res.headers['Location']

    # Intentar acceder a inventario sin sesión
    res2 = client.get('/inventory/', follow_redirects=False)
    assert res2.status_code in (301, 302)
    assert '/auth/login' in res2.headers['Location']

def test_login_and_admin_access(client):
    # 1. Registrar admin inicial
    res_reg = client.post('/auth/register', data={
        "username": "superadmin",
        "password": "Password123!"
    }, follow_redirects=True)
    assert res_reg.status_code == 200

    # 2. Iniciar sesión como superadmin
    res_login = client.post('/auth/login', data={
        "username": "superadmin",
        "password": "Password123!"
    }, follow_redirects=True)
    assert res_login.status_code == 200
    assert b"Has iniciado sesi" in res_login.data

    # 3. Acceder al dashboard
    res_dash = client.get('/')
    assert res_dash.status_code == 200

    # 4. Acceder al módulo de auditoría
    res_audit = client.get('/audit')
    assert res_audit.status_code == 200
