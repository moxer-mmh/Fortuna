import pytest
from finance_manager.core import AccountManager, Category, ExpenseManager, IncomeManager


@pytest.fixture
def account_manager():
    return AccountManager()


@pytest.fixture
def expense_manager():
    return ExpenseManager()


@pytest.fixture
def income_manager():
    return IncomeManager()


@pytest.fixture
def category():
    return Category("Test Category", 1000)
