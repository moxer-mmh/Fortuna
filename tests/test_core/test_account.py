import pytest
from unittest.mock import MagicMock, patch
from finance_manager.core import Account, AccountManager


@pytest.fixture
def mock_db():
    with patch("finance_manager.core.account.DatabaseConnection") as mock:
        db_instance = mock.return_value
        db_instance.fetch_one = MagicMock(return_value=None)
        db_instance.fetch_all = MagicMock(return_value=[])
        db_instance.execute_query = MagicMock()
        yield db_instance


class TestAccount:
    def test_init(self, mock_db):
        account = Account("Savings", 1000)
        assert account.name == "Savings"
        assert account.balance == 1000
        assert account.id is not None

    def test_deposit(self, mock_db):
        account = Account("Checking", 500)
        account.deposit(200)
        assert account.balance == 700
        mock_db.execute_query.assert_called()

    def test_deposit_negative_amount(self, mock_db):
        account = Account("Checking", 500)
        with pytest.raises(ValueError):
            account.deposit(-100)

    def test_withdraw(self, mock_db):
        account = Account("Checking", 500)
        account.withdraw(200)
        assert account.balance == 300
        mock_db.execute_query.assert_called()

    def test_withdraw_insufficient_funds(self, mock_db):
        account = Account("Checking", 500)
        with pytest.raises(ValueError):
            account.withdraw(600)

    def test_transfer(self, mock_db):
        account1 = Account("Savings", 1000)
        account2 = Account("Checking", 500)
        account1.transfer(300, account2)
        assert account1.balance == 700
        assert account2.balance == 800
        assert mock_db.execute_query.call_count >= 2

    def test_get_by_name(self, mock_db):
        mock_db.fetch_one.return_value = ("123", "Savings", 1000.0)
        account = Account.get_by_name("Savings")
        assert account is not None
        assert account.name == "Savings"
        assert account.balance == 1000.0
        assert account.id == "123"

    def test_get_by_id(self, mock_db):
        mock_db.fetch_one.return_value = ("123", "Savings", 1000.0)
        account = Account.get_by_id("123")
        assert account is not None
        assert account.name == "Savings"
        assert account.balance == 1000.0
        assert account.id == "123"


class TestAccountManager:
    @pytest.fixture
    def account_manager(self, mock_db):
        return AccountManager()

    def test_add_account(self, account_manager, mock_db):
        mock_db.fetch_one.return_value = None
        account_manager.add_account("Savings", 1000)
        mock_db.execute_query.assert_called()

    def test_add_existing_account(self, account_manager, mock_db):
        mock_db.fetch_one.return_value = ("123", "Savings", 1000.0)
        with pytest.raises(ValueError):
            account_manager.add_account("Savings", 1000)

    def test_get_account(self, account_manager, mock_db):
        mock_db.fetch_one.return_value = ("123", "Checking", 500.0)
        account = account_manager.get_account("Checking")
        assert account.name == "Checking"
        assert account.balance == 500.0

    def test_get_all_accounts(self, account_manager, mock_db):
        mock_db.fetch_all.return_value = [
            ("123", "Savings", 1000.0),
            ("456", "Checking", 500.0),
        ]
        accounts = account_manager.get_all_accounts()
        assert len(accounts) == 2
        assert accounts[0].name == "Savings"
        assert accounts[1].name == "Checking"

    @pytest.mark.parametrize(
        "inputs,expected_calls",
        [
            (
                ["Savings", "New Savings", "1500"],
                [("Savings",), ("123", "New Savings", 1500.0)],
            ),
        ],
    )
    def test_edit_account(
        self, account_manager, mock_db, monkeypatch, inputs, expected_calls
    ):
        mock_db.fetch_one.return_value = ("123", "Savings", 1000.0)
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))
        account_manager.edit_account()
        assert mock_db.execute_query.called

    def test_delete_account(self, account_manager, mock_db, monkeypatch):
        mock_db.fetch_one.return_value = ("123", "Checking", 500.0)
        monkeypatch.setattr("builtins.input", lambda _: "Checking")
        account_manager.delete_account()
        mock_db.execute_query.assert_called_with(
            "DELETE FROM accounts WHERE id = ?", ("123",)
        )

    def test_transfer_between_accounts(self, account_manager, mock_db, monkeypatch):
        def mock_fetch_one(query, params):
            if params[0] == "Savings":
                return ("123", "Savings", 1000.0)
            elif params[0] == "Checking":
                return ("456", "Checking", 500.0)
            return None

        mock_db.fetch_one.side_effect = mock_fetch_one
        inputs = iter(["Savings", "Checking", "300"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        account_manager.transfer_between_accounts()
        assert mock_db.execute_query.call_count >= 2
