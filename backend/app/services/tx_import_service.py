from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Type, final, override
from datetime import datetime
import pandas as pd

from app.models.transaction_models import Transaction, TransactionType
from app.models.tx_import_models import ThirdParty, TxImportRes
from app.repo.transaction_repo import TransactionRepo


class TxImportRegistry:
    _registry: dict[ThirdParty, Type[TxImportService]] = {}

    @classmethod
    def get(
        cls,
        third_party: ThirdParty,
        df: pd.DataFrame,
        repo: TransactionRepo,
    ) -> TxImportService | None:
        if (import_service := cls._registry.get(third_party)) is None:
            return None

        return import_service(df, repo)

    @classmethod
    def register(
        cls,
        third_party: ThirdParty,
        import_service: Type[TxImportService],
    ) -> None:
        cls._registry[third_party] = import_service


class TxImportService(ABC):
    @abstractmethod
    def __init__(self, df: pd.DataFrame, repo: TransactionRepo):
        pass

    @abstractmethod
    def import_csv(self) -> TxImportRes:
        """
        Returns:
            list[str]: Return a list of transaction record ids
        """
        pass


@final
class PayPayImport(TxImportService):
    @override
    def __init__(self, df: pd.DataFrame, repo: TransactionRepo):
        self.repo = repo
        self.datetime_format = "%Y/%m/%d %H:%M:%S"
        self.records = df.to_dict(orient="records")

    def process_amount(self, record: dict[Any, Any]) -> tuple[float, str]:
        amount = 0
        selected = ""
        for key in (
            "Amount Incoming (Yen)",
            "Amount Outgoing (Yen)",
            "Amount Outgoing Overseas",
        ):
            if record[key] != "-":
                amount = float(record[key].replace(",", ""))
                selected = key
                if selected == "Amount Outgoing Overseas":
                    amount *= float(record["Exchange Rate (Yen)"])

        return amount, selected

    def process_exchange_rate(self, rate: str):
        if rate == "-":
            return None
        else:
            return rate

    def process_tx_type(self, tx_type: str):
        if tx_type in ["Amount Outgoing Overseas", "Amount Outgoing (Yen)"]:
            return TransactionType.EXPENSE
        else:
            return TransactionType.INCOME

    def process_datetime(self, datetime_str: str) -> datetime:
        return datetime.strptime(datetime_str.strip(), self.datetime_format)

    @override
    def import_csv(self) -> TxImportRes:
        transaction_ids: list[str] = []
        for record in self.records:
            amount, tx_type = self.process_amount(record)
            tx_type = self.process_tx_type(tx_type)
            occurred_at = self.process_datetime(record["Date & Time"])
            transaction = Transaction(
                category=None,
                transaction_type=tx_type,
                amount=amount,
                exchange_rate=None,
                description=None,
                occurred_at=occurred_at,
                payment_method=record["Method"],
                business_name=record["Business Name"],
            )

            self.repo.create(TransactionType.EXPENSE, transaction)
            transaction_ids.append(str(transaction.id))
        return TxImportRes(transaction_ids=transaction_ids)


TxImportRegistry.register(ThirdParty.PayPay, PayPayImport)
