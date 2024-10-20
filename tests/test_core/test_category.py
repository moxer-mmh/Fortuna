import pytest
from unittest.mock import MagicMock, patch
from finance_manager.core import Category


@pytest.fixture
def mock_db():
    with patch("finance_manager.core.category.DatabaseConnection") as mock:
        db_instance = mock.return_value
        db_instance.fetch_one = MagicMock(return_value=None)
        db_instance.fetch_all = MagicMock(return_value=[])
        db_instance.execute_query = MagicMock()
        yield db_instance


class TestCategory:
    @pytest.fixture
    def category(self, mock_db):
        return Category(name="Test Category", budget=1000.0, type="expense")

    def test_init(self, category):
        assert isinstance(category.id, str)
        assert category.name == "Test Category"
        assert category.budget == 1000.0
        assert category.type == "expense"

    def test_save(self, category, mock_db):
        category.save()
        mock_db.execute_query.assert_called_once()
        call_args = mock_db.execute_query.call_args[0]
        assert "INSERT OR REPLACE INTO categories" in call_args[0]
        assert len(call_args[1]) == 4

    def test_get_transactions_from_category(self, category, mock_db):
        mock_db.fetch_all.return_value = [
            ("trans123", "2024-01-01", 100.0, "Transaction 1", "acc123"),
            ("trans456", "2024-01-02", 200.0, "Transaction 2", "acc456"),
        ]

        transactions = category.get_transactions_from_category()
        assert len(transactions) == 2
        assert transactions[0].amount == 100.0
        assert transactions[1].amount == 200.0

    def test_get_total_transactions_in_category(self, category, mock_db):
        mock_db.fetch_one.return_value = (300.0,)
        total = category.get_total_transactions_in_category()
        assert total == 300.0

    def test_get_total_transactions_in_category_no_transactions(
        self, category, mock_db
    ):
        mock_db.fetch_one.return_value = (None,)
        total = category.get_total_transactions_in_category()
        assert total == 0.0

    def test_get_by_id(self, mock_db):
        mock_db.fetch_one.return_value = ("cat123", "Test Category", 1000.0, "expense")

        category = Category.get_by_id("cat123")
        assert category is not None
        assert category.id == "cat123"
        assert category.name == "Test Category"
        assert category.budget == 1000.0
        assert category.type == "expense"

    def test_get_by_id_not_found(self, mock_db):
        mock_db.fetch_one.return_value = None
        category = Category.get_by_id("nonexistent")
        assert category is None

    def test_get_by_name(self, mock_db):
        mock_db.fetch_one.return_value = ("cat123", "Test Category", 1000.0, "expense")

        category = Category.get_by_name("Test Category", "expense")
        assert category is not None
        assert category.name == "Test Category"
        assert category.type == "expense"

    def test_get_by_name_not_found(self, mock_db):
        mock_db.fetch_one.return_value = None
        category = Category.get_by_name("nonexistent", "expense")
        assert category is None

    def test_str_representation(self, category):
        assert str(category) == "Test Category (Budget: 1000.00 DA)"

    def test_repr_representation(self, category):
        assert (
            repr(category)
            == "Category(name='Test Category', budget=1000.0, type='expense')"
        )
