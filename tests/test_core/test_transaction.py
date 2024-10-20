import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from finance_manager.core import Transaction


@pytest.fixture
def mock_db():
    with patch("finance_manager.core.transaction.DatabaseConnection") as mock:
        db_instance = mock.return_value
        db_instance.fetch_one = MagicMock(return_value=None)
        db_instance.execute_query = MagicMock()
        yield db_instance


class TestTransaction:
    @pytest.fixture
    def transaction(self, mock_db):
        return Transaction(
            date=datetime(2024, 1, 1),
            amount=100.0,
            description="Test transaction",
            account_id="acc123",
            category_id="cat456",
            type="expense",
        )

    def test_init(self, transaction):
        assert isinstance(transaction.id, str)
        assert transaction.date == datetime(2024, 1, 1)
        assert transaction.amount == 100.0
        assert transaction.description == "Test transaction"
        assert transaction.account_id == "acc123"
        assert transaction.category_id == "cat456"
        assert transaction.type == "expense"

    def test_init_with_string_date(self, mock_db):
        transaction = Transaction(
            date="2024-01-01",
            amount=100.0,
            description="Test transaction",
            account_id="acc123",
        )
        assert isinstance(transaction.date, datetime)
        assert transaction.date == datetime(2024, 1, 1)

    def test_save(self, transaction, mock_db):
        transaction.save()
        mock_db.execute_query.assert_called_once()
        call_args = mock_db.execute_query.call_args[0]
        assert "INSERT OR REPLACE INTO transactions" in call_args[0]
        assert len(call_args[1]) == 7

    def test_get_by_id(self, mock_db):
        mock_db.fetch_one.return_value = (
            "trans123",
            "2024-01-01",
            100.0,
            "Test transaction",
            "acc123",
            "cat456",
            "expense",
        )

        transaction = Transaction.get_by_id("trans123")
        assert transaction is not None
        assert transaction.id == "trans123"
        assert transaction.amount == 100.0
        assert transaction.description == "Test transaction"

    def test_get_by_id_not_found(self, mock_db):
        mock_db.fetch_one.return_value = None
        transaction = Transaction.get_by_id("nonexistent")
        assert transaction is None

    def test_delete(self, transaction, mock_db):
        transaction.delete()
        mock_db.execute_query.assert_called_once_with(
            "DELETE FROM transactions WHERE id = ?", (transaction.id,)
        )

    def test_str_representation(self, transaction):
        expected = f"(id='{transaction.id}' - date='2024-01-01' - amount=100.00)"
        assert str(transaction) == expected

    def test_repr_representation(self, transaction):
        assert repr(transaction) == str(transaction)
