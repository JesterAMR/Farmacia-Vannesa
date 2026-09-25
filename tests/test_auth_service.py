def test_auth_bootstrap_first_admin(services):
    auth = services["auth"]
    # Primer usuario registrado debe ser admin
    success = auth.register("admin_user", "SecurePass123!")
    assert success is True

    user = auth.login("admin_user", "SecurePass123!")
    assert user is not None
    assert user.role == "admin"
    assert user.username == "admin_user"

def test_auth_subsequent_user_cajero(services):
    auth = services["auth"]
    auth.register("admin_boss", "Pass123!")
    # Segundo usuario sin rol explícito debe ser cajero
    success = auth.register("cajero_juan", "Pass456!")
    assert success is True

    user = auth.login("cajero_juan", "Pass456!")
    assert user is not None
    assert user.role == "cajero"

def test_auth_duplicate_username_fails(services):
    auth = services["auth"]
    auth.register("usuario_unico", "Pass123!")
    # Duplicado debe retornar False
    success = auth.register("usuario_unico", "OtraPass789!")
    assert success is False

def test_auth_invalid_password_fails(services):
    auth = services["auth"]
    auth.register("usuario_test", "ClaveCorrecta")
    user = auth.login("usuario_test", "ClaveEquivocada")
    assert user is None
