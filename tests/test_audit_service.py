def test_audit_logging_and_retrieval(services):
    audit = services["audit"]

    log1 = audit.log_action("Inicio de sesión", user_id=1, details="Acceso desde navegador")
    assert log1.id is not None
    assert log1.action == "Inicio de sesión"

    log2 = audit.log_action("Creó medicamento", user_id=1, details="Paracetamol 500mg (+100 unid)")
    assert log2.id is not None

    recent = audit.get_recent_logs(limit=10)
    assert len(recent) >= 2
    actions = [l.action for l in recent]
    assert "Inicio de sesión" in actions
    assert "Creó medicamento" in actions
