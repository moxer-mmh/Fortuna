import pytest
from datetime import datetime
from finance_manager.core import Income, IncomeManager, Category, Account


class TestIncome:
    @pytest.fixture
    def income(self):
        category = Category("Salary", 5000)
        account = Account("Checking", 1000)
        return Income.add_income(
            datetime.now(), 3000, "Monthly salary", category, account
        )

    def test_init(self, income):
        assert isinstance(income.transaction.date, datetime)
        assert income.transaction.amount == 3000
        assert income.transaction.description == "Monthly salary"
        assert income.category.name == "Salary"
        assert income.account.name == "Checking"

    def test_edit(self, income):
        new_category = Category("Bonus", 1000)
        income.edit(
            new_amount=3500, new_description="Salary + bonus", new_category=new_category
        )
        assert income.transaction.amount == 3500
        assert income.transaction.description == "Salary + bonus"
        assert income.category.name == "Bonus"

    def test_delete(self, income):
        initial_balance = income.account.balance
        income.delete()
        assert income.category.get_total_transactions_in_category() == 0
        assert income.account.balance == initial_balance - income.transaction.amount


class TestIncomeManager:
    @pytest.fixture
    def income_manager(self):
        return IncomeManager()

    def test_add_income(self, income_manager):
        category = Category("Freelance", 2000)
        account = Account("Savings", 5000)
        income_manager.add_income(
            Income.add_income(
                datetime.now(), 500, "Web design project", category, account
            )
        )
        assert len(income_manager.incomes) == 1

    def test_get_income(self, income_manager):
        category = Category("Investment", 1000)
        account = Account("Investment Account", 10000)
        income = Income.add_income(datetime.now(), 200, "Dividend", category, account)
        income_manager.add_income(income)
        retrieved_income = income_manager.get_income(income.transaction.id)
        assert retrieved_income == income

    def test_display_incomes(self, income_manager, capsys):
        category = Category("Rent", 1500)
        account = Account("Real Estate", 50000)
        income_manager.add_income(
            Income.add_income(datetime.now(), 1000, "Apartment rent", category, account)
        )
        income_manager.display_incomes()
        captured = capsys.readouterr()
        assert "Apartment rent" in captured.out
        assert "1000.00" in captured.out
