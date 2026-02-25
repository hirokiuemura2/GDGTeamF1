from typing import override


class TransactionError(Exception):
    """Base class for transaction error"""


class TransactionNotExists(TransactionError):
    @override
    def __str__(self):
        return "The target transaction does not exist."
