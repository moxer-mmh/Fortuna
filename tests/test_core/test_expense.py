import pytest
from datetime import datetime
from finance_manager.core import Expense, ExpenseManager, Category, Account


class TestExpense:
    @pytest.fixture
    def expense(self):
        category = Category("Food", 500)
        account = Account("Checking", 1000)
        return Expense.add_expense(datetime.now(), 50, "Lunch", category, account)

    def test_init(self, expense):
        assert isinstance(expense.transaction.date, datetime)
        assert expense.transaction.amount == 50
        assert expense.transaction.description == "Lunch"
        assert expense.category.name == "Food"
        assert expense.account.name == "Checking"

    def test_edit(self, expense):
        new_category = Category("Dining Out", 300)
        expense.edit(new_amount=60, new_description="Dinner", new_category=new_category)
        assert expense.transaction.amount == 60
        assert expense.transaction.description == "Dinner"
        assert expense.category.name == "Dining Out"

    def test_delete(self, expense):
        initial_balance = expense.account.balance
        expense.delete()
        assert expense.category.get_total_transactions_in_category() == 0
        assert expense.account.balance == initial_balance + expense.transaction.amount


class TestExpenseManager:
    @pytest.fixture
    def expense_manager(self):
        return ExpenseManager()

    def test_add_expense(self, expense_manager):
        category = Category("Groceries", 400)
        account = Account("Savings", 2000)
        expense_manager.add_expense(
            Expense.add_expense(datetime.now(), 100, "Supermarket", category, account)
        )
        assert len(expense_manager.expenses) == 1

    def test_get_expense(self, expense_manager):
        category = Category("Transport", 200)
        account = Account("Cash", 500)
        expense = Expense.add_expense(
            datetime.now(), 30, "Bus ticket", category, account
        )
        expense_manager.add_expense(expense)
        retrieved_expense = expense_manager.get_expense(expense.transaction.id)
        assert retrieved_expense == expense

    def test_display_expenses(self, expense_manager, capsys):
        category = Category("Entertainment", 300)
        account = Account("Credit Card", 1000)
        expense_manager.add_expense(
            Expense.add_expense(datetime.now(), 50, "Cinema", category, account)
        )
        expense_manager.display_expenses()
        captured = capsys.readouterr()
        assert "Cinema" in captured.out
        assert "50.00" in captured.out
