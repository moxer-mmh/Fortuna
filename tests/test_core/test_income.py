# import pytest
# from unittest.mock import MagicMock, patch
# from datetime import datetime
# from finance_manager.core import Income, IncomeManager, Category, Account, Transaction


# @pytest.fixture
# def mock_db():
#     with patch("finance_manager.core.income.DatabaseConnection") as mock:
#         db_instance = mock.return_value
#         db_instance.fetch_one = MagicMock(return_value=None)
#         db_instance.fetch_all = MagicMock(return_value=[])
#         db_instance.execute_query = MagicMock()
#         yield db_instance


# class TestIncome:
#     @pytest.fixture
#     def category(self, mock_db):
#         return Category(name="Salary", budget=5000.0, type="income", id="cat123")

#     @pytest.fixture
#     def account(self, mock_db):
#         return Account(name="Checking", balance=1000.0, id="acc123")

#     @pytest.fixture
#     def transaction(self, mock_db):
#         return Transaction(
#             date=datetime(2024, 1, 1),
#             amount=3000.0,
#             description="Monthly salary",
#             account_id="acc123",
#             category_id="cat123",
#             type="income",
#             id="trans123",
#         )

#     @pytest.fixture
#     def income(self, transaction, category, account, mock_db):
#         return Income(transaction, category, account)

#     def test_init(self, income):
#         assert income.transaction.type == "income"
#         assert income.transaction.category_id == income.category.id
#         assert income.transaction.account_id == income.account.id

#     def test_save(self, income, mock_db):
#         with patch.object(income.account, "deposit") as mock_deposit:
#             income.save()
#             mock_deposit.assert_called_once_with(income.transaction.amount)

#     def test_delete(self, income, mock_db):
#         with patch.object(income.account, "withdraw") as mock_withdraw:
#             income.delete()
#             mock_withdraw.assert_called_once_with(income.transaction.amount)

#     def test_add_income(self, category, account, mock_db):
#         income = Income.add_income(
#             date=datetime(2024, 1, 1),
#             amount=3000.0,
#             description="Monthly salary",
#             category=category,
#             account=account,
#         )
#         assert isinstance(income, Income)
#         assert income.transaction.amount == 3000.0
#         assert income.transaction.type == "income"

#     def test_str_representation(self, income):
#         expected = (
#             f"Income: {income.transaction} - "
#             f"Description: {income.transaction.description} - "
#             f"Category: {income.category.name} - "
#             f"Account: {income.account.name}"
#         )
#         assert str(income) == expected


# class TestIncomeManager:
#     @pytest.fixture
#     def income_manager(self):
#         return IncomeManager()

#     @pytest.fixture
#     def mock_db(self):
#         with patch("finance_manager.database.DatabaseConnection") as mock:
#             yield mock.return_value

#     @pytest.fixture
#     def category(self):
#         category = Category(name="Salary", budget=5000.0, type="income", id="cat123")
#         return category

#     @pytest.fixture
#     def account(self):
#         account = Account(name="Checking", balance=1000.0, id="acc123")
#         return account

#     def test_add_income(self, income_manager, mock_db):
#         income = MagicMock()
#         income_manager.add_income(income)
#         income.save.assert_called_once()

#     # def test_add_category(self, mock_db, income_manager):
#     #     mock_db_instance = mock_db.return_value
#     #     mock_db_instance.fetch_one.return_value = None

#     #     income_manager.add_category("Salary", 5000.0)

#     #     mock_db_instance.execute_query.assert_called_once_with(
#     #         "INSERT INTO categories (name, budget, type) VALUES (?, ?, 'income')",
#     #         ("Salary", 5000.0),
#     #     )

#     def test_add_category_already_exists(self, income_manager, mock_db):
#         mock_db.fetch_one.return_value = ("cat123", "Salary", 5000.0, "income")
#         with pytest.raises(ValueError):
#             income_manager.add_category("Salary", 5000.0)

#     def test_get_income(self, income_manager, mock_db):
#         transaction_data = (
#             "trans123",
#             "2024-01-01",
#             3000.0,
#             "Monthly salary",
#             "acc123",
#             "cat123",
#             "income",
#         )
#         mock_transaction = Transaction(
#             date=datetime(2024, 1, 1),
#             amount=3000.0,
#             description="Monthly salary",
#             account_id="acc123",
#             category_id="cat123",
#             type="income",
#             id="trans123",
#         )

#         mock_category = Category(
#             name="Salary", budget=5000.0, type="income", id="cat123"
#         )

#         mock_account = Account(name="Checking", balance=1000.0, id="acc123")

#         with patch(
#             "finance_manager.core.transaction.Transaction.get_by_id",
#             return_value=mock_transaction,
#         ):
#             with patch(
#                 "finance_manager.core.category.Category.get_by_id",
#                 return_value=mock_category,
#             ):
#                 with patch(
#                     "finance_manager.core.account.Account.get_by_id",
#                     return_value=mock_account,
#                 ):
#                     income = income_manager.get_income("trans123")
#                     assert income is not None
#                     assert income.transaction.amount == 3000.0
#                     assert income.category.name == "Salary"
#                     assert income.account.name == "Checking"

#     # def test_get_all_categories(self, income_manager, mock_db):
#     #     mock_db.fetch_all.return_value = [
#     #         (1, "Salary", 5000.0, "income"),
#     #         (2, "Bonus", 1000.0, "income"),
#     #     ]

#     #     categories = income_manager.get_all_categories()
#     #     assert len(categories) == 2
#     #     assert categories[0].name == "Salary"
#     #     assert categories[1].name == "Bonus"

#     # def test_get_all_incomes(self, income_manager, mock_db):
#     #     mock_db.fetch_all.return_value = [
#     #         (
#     #             "trans123",
#     #             "2024-01-01",
#     #             3000.0,
#     #             "Monthly salary",
#     #             "cat123",
#     #             "acc123",
#     #             "income",
#     #         )
#     #     ]

#     #     incomes = income_manager.get_all_incomes()
#     #     assert len(incomes) == 1
#     #     assert incomes[0].transaction.amount == 3000.0
#     #     assert incomes[0].category.id == "cat123"
#     #     assert incomes[0].account.id == "acc123"
