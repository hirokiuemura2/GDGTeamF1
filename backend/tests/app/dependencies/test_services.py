def test_get_expense_service_constructs_with_deps(firestore_db):
    from app.dependencies import services as svc_dep
    from app.services.expense_service import ExpenseService

    # Use real dependencies with the test Firestore client
    svc = svc_dep.get_expense_service(db=firestore_db, user_id="test-user")

    # Verify we get a real ExpenseService instance
    assert isinstance(svc, ExpenseService)

    # Verify the service is functional by checking its repo
    assert svc.repo is not None
    assert svc.repo.col is not None

