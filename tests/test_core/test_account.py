import pytest
from finance_manager.core import Account, AccountManager


class TestAccount:
    def test_init(self):
        account = Account("Savings", 1000)
        assert account.name == "Savings"
        assert account.balance == 1000

    def test_deposit(self):
        account = Account("Checking", 500)
        account.deposit(200)
        assert account.balance == 700

    def test_deposit_negative_amount(self):
        account = Account("Checking", 500)
        with pytest.raises(ValueError):
            account.deposit(-100)

    def test_withdraw(self):
        account = Account("Checking", 500)
        account.withdraw(200)
        assert account.balance == 300

    def test_withdraw_insufficient_funds(self):
        account = Account("Checking", 500)
        with pytest.raises(ValueError):
            account.withdraw(600)

    def test_transfer(self):
        account1 = Account("Savings", 1000)
        account2 = Account("Checking", 500)
        account1.transfer(300, account2)
        assert account1.balance == 700
        assert account2.balance == 800


class TestAccountManager:
    @pytest.fixture
    def account_manager(self):
        return AccountManager()

    def test_add_account(self, account_manager):
        account_manager.add_account("Savings", 1000)
        assert len(account_manager.accounts) == 1
        assert account_manager.accounts[0].name == "Savings"
        assert account_manager.accounts[0].balance == 1000

    def test_get_account(self, account_manager):
        account_manager.add_account("Checking", 500)
        account = account_manager.get_account("Checking")
        assert account.name == "Checking"
        assert account.balance == 500

    def test_get_nonexistent_account(self, account_manager):
        assert account_manager.get_account("Nonexistent") is None

    def test_edit_account(self, account_manager, monkeypatch):
        account_manager.add_account("Savings", 1000)
        monkeypatch.setattr("builtins.input", lambda _: "Savings")
        monkeypatch.setattr("builtins.input", lambda _: "New Savings")
        monkeypatch.setattr("builtins.input", lambda _: "1500")
        account_manager.edit_account()
        account = account_manager.get_account("New Savings")
        assert account.name == "New Savings"
        assert account.balance == 1500

    def test_delete_account(self, account_manager, monkeypatch):
        account_manager.add_account("Checking", 500)
        monkeypatch.setattr("builtins.input", lambda _: "Checking")
        account_manager.delete_account()
        assert len(account_manager.accounts) == 0

    def test_transfer_between_accounts(self, account_manager, monkeypatch):
        account_manager.add_account("Savings", 1000)
        account_manager.add_account("Checking", 500)
        monkeypatch.setattr("builtins.input", lambda _: "Savings")
        monkeypatch.setattr("builtins.input", lambda _: "Checking")
        monkeypatch.setattr("builtins.input", lambda _: "300")
        account_manager.transfer_between_accounts()
        savings = account_manager.get_account("Savings")
        checking = account_manager.get_account("Checking")
        assert savings.balance == 700
        assert checking.balance == 800
