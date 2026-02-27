def test_get_transaction_services_construct_with_deps(firestore_db):
    from app.dependencies import services as svc_dep
    from app.services.transaction_service import TransactionService

    transaction_svc = svc_dep.get_transaction_service(
        db=firestore_db, user_id="test-user"
    )

    assert isinstance(transaction_svc, TransactionService)

    assert transaction_svc.repo is not None
