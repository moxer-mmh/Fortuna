import pytest
from finance_manager.core import Category, Transaction
from datetime import datetime


class TestCategory:
    def test_init(self):
        category = Category("Groceries", 500)
        assert category.name == "Groceries"
        assert category.budget == 500
        assert len(category.transactions) == 0

    def test_add_transaction_to_category(self):
        category = Category("Entertainment", 200)
        transaction = Transaction(datetime.now(), 50, "Movie ticket")
        category.add_transaction_to_category(transaction)
        assert len(category.transactions) == 1
        assert category.transactions[0] == transaction

    def test_delete_transaction_from_category(self):
        category = Category("Food", 300)
        transaction = Transaction(datetime.now(), 25, "Lunch")
        category.add_transaction_to_category(transaction)
        category.delete_transaction_from_category(transaction)
        assert len(category.transactions) == 0

    def test_get_total_transactions_in_category(self):
        category = Category("Shopping", 1000)
        category.add_transaction_to_category(
            Transaction(datetime.now(), 200, "Clothes")
        )
        category.add_transaction_to_category(Transaction(datetime.now(), 150, "Shoes"))
        assert category.get_total_transactions_in_category() == 350

    def test_str_representation(self):
        category = Category("Utilities", 400)
        assert str(category) == "Utilities (Budget: 400.00 DA)"

    def test_repr_representation(self):
        category = Category("Travel", 2000)
        assert repr(category) == "Category(name='Travel', budget=2000)"
