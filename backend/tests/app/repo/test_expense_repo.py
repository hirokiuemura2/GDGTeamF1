def test_create_expense_writes_and_returns_id(firestore_db):
    from app.repo.expense_repo import ExpenseRepo

    repo = ExpenseRepo(firestore_db, "test-user")

    payload = {"amount": 1.0, "currency": "USD"}
    expense_id = repo.create_expense(payload)

    # Verify the expense was created with a generated ID
    assert expense_id is not None
    assert len(expense_id) > 0

    # Verify the data was written to Firestore
    doc_ref = (
        firestore_db.collection("users")
        .document("test-user")
        .collection("expenses")
        .document(expense_id)
    )
    doc = doc_ref.get()

    assert doc.exists
    assert doc.to_dict() == payload

