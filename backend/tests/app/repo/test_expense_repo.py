class FakeDocRef:
    def __init__(self, id_: str = "doc_1"):
        self.id = id_
        self.data = None

    def set(self, data):
        self.data = data


class FakeCollection:
    def __init__(self, id_: str = "col"):
        self._id = id_
        self._next_doc = FakeDocRef("generated_id")

    def document(self):
        return self._next_doc


class FakeUserDoc:
    def __init__(self):
        self._expenses = FakeCollection("expenses")

    def collection(self, name):
        assert name == "expenses"
        return self._expenses


class FakeUsersCollection:
    def __init__(self):
        self._user_doc = FakeUserDoc()

    def document(self, user_id):
        assert user_id == "user"
        return self._user_doc


class FakeDB:
    def __init__(self):
        self._users = FakeUsersCollection()

    def collection(self, name):
        assert name == "users"
        return self._users


def test_create_expense_writes_and_returns_id():
    from app.repo.expense_repo import ExpenseRepo

    db = FakeDB()
    repo = ExpenseRepo(db, "user")

    payload = {"amount": 1.0, "currency": "USD"}
    expense_id = repo.create_expense(payload)

    assert expense_id == "generated_id"
    # Ensure data was written to the fake doc
    assert db._users._user_doc._expenses._next_doc.data == payload

