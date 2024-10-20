# import pytest
# from datetime import datetime
# from unittest.mock import MagicMock, patch
# from decimal import Decimal
# from finance_manager.core import Expense, ExpenseManager, Category, Account, Transaction


# class TestExpense:
#     @pytest.fixture
#     def mock_db(self):
#         return MagicMock()

#     @pytest.fixture
#     def category(self):
#         category = Category(name="Food", budget=500.0, type="expense")
#         category.id = 1
#         return category

#     @pytest.fixture
#     def account(self):
#         account = Account(name="Checking", balance=1000.0)
#         account.id = 1
#         return account

#     @pytest.fixture
#     def transaction(self, category, account):
#         return Transaction(
#             date=datetime(2024, 1, 1),
#             amount=100.0,
#             description="Test expense",
#             account_id="acc123",
#             category_id="cat123",
#             type="expense",
#             id="trans123",
#         )

#     @pytest.fixture
#     def expense(self, transaction, category, account):
#         return Expense(transaction, category, account)

#     def test_expense_initialization(self, expense):
#         assert expense.transaction.type == "expense"
#         assert expense.category.name == "Food"
#         assert expense.account.name == "Checking"
#         assert expense.transaction.amount == 50.0

#     def test_save_expense(self, expense):
#         with patch.object(expense.transaction, "save") as mock_save:
#             with patch.object(expense.account, "withdraw") as mock_withdraw:
#                 expense.save()
#                 mock_save.assert_called_once()
#                 mock_withdraw.assert_called_once_with(50.0)

#     def test_delete_expense(self, expense):
#         with patch.object(expense.transaction, "delete") as mock_delete:
#             with patch.object(expense.account, "deposit") as mock_deposit:
#                 expense.delete()
#                 mock_delete.assert_called_once()
#                 mock_deposit.assert_called_once_with(50.0)

#     def test_add_expense_classmethod(self, category, account):
#         date = datetime.now()
#         expense = Expense.add_expense(
#             date=date,
#             amount=75.0,
#             description="Dinner",
#             category=category,
#             account=account,
#         )
#         assert expense.transaction.date == date
#         assert expense.transaction.amount == 75.0
#         assert expense.transaction.description == "Dinner"
#         assert expense.category == category
#         assert expense.account == account


# class TestExpenseManager:
#     @pytest.fixture
#     def expense_manager(self):
#         return ExpenseManager()

#     @pytest.fixture
#     def mock_db(self):
#         with patch("finance_manager.database.DatabaseConnection") as mock:
#             yield mock.return_value

#     @pytest.fixture
#     def category(self):
#         category = Category(name="Groceries", budget=400.0, type="expense")
#         category.id = 1
#         return category

#     @pytest.fixture
#     def account(self):
#         account = Account(name="Savings", balance=2000.0)
#         account.id = 1
#         return account

#     def test_add_category(self, expense_manager, mock_db):
#         with patch.object(Category, "get_by_name", return_value=None):
#             with patch.object(Category, "save"):
#                 expense_manager.add_category("Food", 500.0)

#     def test_add_category_duplicate(self, expense_manager):
#         with patch.object(
#             Category,
#             "get_by_name",
#             return_value=Category(name="Food", budget=500.0, type="expense"),
#         ):
#             with pytest.raises(ValueError):
#                 expense_manager.add_category("Food", 500.0)

#     def test_get_expense(self, expense_manager, category, account):
#         transaction = Transaction(
#             date=datetime.now(),
#             amount=100.0,
#             description="Test expense",
#             account_id=account.id,
#             category_id=category.id,
#             type="expense",
#             id="123",
#         )

#         with patch.object(Transaction, "get_by_id", return_value=transaction):
#             with patch.object(Category, "get_by_id", return_value=category):
#                 with patch.object(Account, "get_by_id", return_value=account):
#                     expense = expense_manager.get_expense("123")
#                     assert expense.transaction == transaction
#                     assert expense.category == category
#                     assert expense.account == account

#     def test_get_all_categories(self, expense_manager, mock_db):
#         test_data = [
#             (1, "Food", 500.0, "expense"),
#             (2, "Transport", 300.0, "expense"),
#         ]

#         mock_db.fetch_all.return_value = test_data

#         with patch(
#             "finance_manager.core.category.DatabaseConnection"
#         ) as mock_category_db:
#             mock_category_db.return_value = mock_db
#             categories = expense_manager.get_all_categories()

#             assert len(categories) == 2
#             assert categories[0].name == "Food"
#             assert categories[1].name == "Transport"

#             mock_db.fetch_all.assert_called_once_with(
#                 "SELECT id, name, budget, type FROM categories WHERE type = 'expense'"
#             )

#     def test_get_all_expenses(self, expense_manager, mock_db):
#         mock_db.fetch_all.return_value = [
#             (
#                 "trans123",
#                 "2024-01-01",
#                 100.0,
#                 "Test expense",
#                 "cat123",
#                 "acc123",
#                 "expense",
#             )
#         ]

#     def test_display_expenses(self, expense_manager, capsys):
#         expense = MagicMock()
#         expense.__str__.return_value = "Test expense display"
#         with patch.object(ExpenseManager, "get_all_expenses", return_value=[expense]):
#             expense_manager.display_expenses()
#             captured = capsys.readouterr()
#             assert "Test expense display" in captured.out

#     def test_edit_expense(self, expense_manager, category, account):
#         expense = Expense.add_expense(
#             datetime.now(), 100.0, "Original expense", category, account
#         )

#         with patch(
#             "builtins.input",
#             side_effect=[
#                 "1",
#                 "2024-01-01",
#                 "150.0",
#                 "Updated expense",
#                 "Updated Category",
#             ],
#         ):
#             with patch.object(ExpenseManager, "get_expense", return_value=expense):
#                 with patch.object(
#                     ExpenseManager, "get_category", return_value=category
#                 ):
#                     expense_manager.edit_expense()
#                     assert expense.transaction.amount == 150.0
#                     assert expense.transaction.description == "Updated expense"

#     def test_delete_category_with_expenses(self, expense_manager, mock_db):
#         category = Category(name="Test Category", budget=500.0, type="expense")
#         category.id = 1

#         expense = MagicMock()
#         expense.delete = MagicMock()

#         with patch.object(
#             ExpenseManager, "get_category", return_value=category
#         ), patch.object(
#             ExpenseManager, "get_all_expenses", return_value=[expense]
#         ), patch(
#             "builtins.input", return_value="Test Category"
#         ):

#             expense_manager.delete_category()

#             expense.delete.assert_called_once()

#             mock_db.execute_query.assert_called_once_with(
#                 "DELETE FROM categories WHERE id = ?", (category.id,)
#             )
