from datetime import datetime
from typing import Any, final

from google.cloud.firestore import Client
from google.cloud.firestore_v1 import FieldFilter
from pydantic import UUID4

from app.errors.transaction import TransactionNotExists
from app.models.transaction_models import Transaction, TransactionType


@final
class TransactionRepo:
    def __init__(self, db: Client, user_id: str):
        user_doc = db.collection("users").document(user_id)
        self.tx_collection = user_doc.collection("transactions")

    @staticmethod
    def _apply_optional_filters(
        query: Any,
        filters: list[tuple[str, str, Any]],
    ) -> Any:
        for field, operator, value in filters:
            if value is None:
                continue
            query = query.where(
                filter=FieldFilter(
                    field,
                    operator,
                    value,
                )
            )
        return query

    @staticmethod
    def _apply_optional_in_filters(
        query: Any,
        filters: list[tuple[str, list[Any] | None]],
    ) -> Any:
        for field, values in filters:
            if values is None or len(values) == 0:
                continue
            query = query.where(
                filter=FieldFilter(
                    field,
                    "in",
                    values,
                )
            )
        return query

    @staticmethod
    def _apply_pagination(
        query: Any,
        offset: int | None,
        limit: int | None,
    ) -> Any:
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query

    @staticmethod
    def _stream_docs(query: Any) -> list[Transaction]:
        docs = query.stream()
        result: list[Transaction] = []
        for doc in docs:
            if not doc.exists:
                continue
            data = doc.to_dict() | {"id": doc.id}
            tx_type = data.get("transaction_type")
            if isinstance(tx_type, str):
                data["transaction_type"] = TransactionType(tx_type)
            result.append(Transaction(**data))
        return result

    def create(
        self, transaction_type: TransactionType, data: Transaction | dict[str, Any]
    ) -> Transaction:
        if isinstance(data, dict):
            # Validate and normalize common transaction fields before persisting.
            data = Transaction(**data)

        tx_data = data.model_dump()
        tx_data["id"] = str(tx_data["id"])
        tx_data["transaction_type"] = tx_data["transaction_type"].value

        doc_ref = self.tx_collection.document(tx_data["id"])
        doc_ref.set(tx_data)
        return data

    def delete(
        self, transaction_type: TransactionType, ids: list[UUID4]
    ) -> list[UUID4]:
        deleted_ids: list[UUID4] = []
        for id in ids:
            doc_ref = self.tx_collection.document(str(id))
            doc = doc_ref.get()
            if not doc.exists:
                continue
            data = doc.to_dict()
            if data.get("transaction_type") != transaction_type.value:
                continue
            doc_ref.delete()
            deleted_ids.append(id)
        return deleted_ids

    def get(self, id: UUID4) -> Transaction:
        doc = self.tx_collection.document(str(id)).get()
        if not doc.exists:
            raise TransactionNotExists()

        return Transaction(**doc.to_dict())

    def list(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Transaction]:
        query = self.tx_collection
        query = query.order_by("occurred_at", direction="DESCENDING")
        query = self._apply_pagination(query, offset=offset, limit=limit)
        return self._stream_docs(query)

    def list_by_category(
        self,
        category: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Transaction]:
        query = self.tx_collection
        query = query.order_by("occurred_at", direction="DESCENDING")
        query = query.where(filter=FieldFilter("category", "==", category))
        query = self._apply_pagination(query, offset, limit)
        return self._stream_docs(query)

    def search(
        self,
        transaction_type: TransactionType,
        id: list[UUID4] | None = None,
        min_amount: int | None = None,
        max_amount: int | None = None,
        currency: Any = None,
        category: Any = None,
        occurred_on: datetime | None = None,
        occurred_before: datetime | None = None,
        occurred_after: datetime | None = None,
        recurring_only: bool | None = None,
        exclude_recurring: bool | None = None,
        subscription_id: str | None = None,
        order_by: str = "occurred_at",
        order_direction: str = "DESCENDING",
        limit: int | None = None,
        offset: int | None = None,
        **_: Any,
    ) -> list[Transaction]:
        if id is not None and len(id) > 0:
            result: list[Transaction] = []
            for tx_id in id:
                doc = self.tx_collection.document(str(tx_id)).get()
                if not doc.exists:
                    continue
                result.append(Transaction(**doc.to_dict()))
            return result

        query = self.tx_collection
        query = query.where(
            filter=FieldFilter("transaction_type", "==", transaction_type.value)
        )

        if occurred_on is not None:
            occurred_after = occurred_on.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            occurred_before = occurred_on.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

        query = self._apply_optional_filters(
            query,
            [
                ("amount", ">=", min_amount),
                ("amount", "<=", max_amount),
                ("occurred_at", "<=", occurred_before),
                ("occurred_at", ">=", occurred_after),
            ],
        )

        # Support either scalar (==) or list (in) for currency/category.
        if isinstance(currency, list):
            query = self._apply_optional_in_filters(query, [("currency", currency)])
        elif currency is not None:
            query = query.where(filter=FieldFilter("currency", "==", str(currency)))

        if isinstance(category, list):
            query = self._apply_optional_in_filters(query, [("category", category)])
        elif category is not None:
            query = query.where(filter=FieldFilter("category", "==", category))

        if transaction_type == TransactionType.EXPENSE:
            if recurring_only:
                query = query.where(filter=FieldFilter("interval", "!=", None))
                if subscription_id is not None:
                    query = query.where(
                        filter=FieldFilter("subscription_id", "==", subscription_id)
                    )
            if exclude_recurring:
                query = query.where(filter=FieldFilter("interval", "==", None))
        query = query.order_by(order_by, direction=order_direction)
        query = self._apply_pagination(query, offset=offset, limit=limit)
        return [
            doc
            for doc in self._stream_docs(query)
            if doc.transaction_type == transaction_type
        ]
