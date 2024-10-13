import pytest
from datetime import datetime
from finance_manager.core import Transaction, Account


class TestTransaction:
    @pytest.fixture
    def transaction(self):
        account = Account("Checking", 1000)
        return Transaction(datetime.now(), 100, "Test transaction", account)

    def test_init(self, transaction):
        assert isinstance(transaction.id, str)
        assert isinstance(transaction.date, datetime)
        assert transaction.amount == 100
        assert transaction.description == "Test transaction"
        assert isinstance(transaction.account, Account)

    def test_str_representation(self, transaction):
        assert str(transaction).startswith("(id='")
        assert "date='" in str(transaction)
        assert "amount=100.00" in str(transaction)

    def test_repr_representation(self, transaction):
        assert repr(transaction) == str(transaction)
