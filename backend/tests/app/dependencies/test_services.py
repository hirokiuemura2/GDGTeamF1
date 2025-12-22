def test_get_expense_service_constructs_with_deps(monkeypatch):
    from app.dependencies import services as svc_dep
    from app.services.expense_service import ExpenseService

    created = {}

    class DummyRepo:
        def __init__(self, db, user_id):
            created["db"] = db
            created["user_id"] = user_id

    # Replace ExpenseRepo inside the services module
    monkeypatch.setattr(svc_dep, "ExpenseRepo", DummyRepo)

    svc = svc_dep.get_expense_service(db="db123", user_id="u1")
    assert isinstance(svc, ExpenseService)
    assert created == {"db": "db123", "user_id": "u1"}

