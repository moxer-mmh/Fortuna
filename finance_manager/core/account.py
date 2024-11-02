# finance_manager/core/account.py
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import Account as AccountModel
from ..database import DatabaseConnection


class Account:
    def __init__(self, name: str, balance: float = 0, id: str = None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.balance = balance
        self._db = DatabaseConnection()

    @classmethod
    def from_orm(cls, db_account: AccountModel) -> "Account":
        """Convert ORM model instance to Account domain object"""
        return cls(name=db_account.name, balance=db_account.balance, id=db_account.id)

    def to_orm(self) -> AccountModel:
        """Convert Account domain object to ORM model instance"""
        return AccountModel(id=self.id, name=self.name, balance=self.balance)

    def save(self) -> None:
        with self._db.get_session() as session:
            db_account = session.query(AccountModel).filter_by(id=self.id).first()
            if db_account:
                db_account.name = self.name
                db_account.balance = self.balance
            else:
                db_account = self.to_orm()
                session.add(db_account)
            session.commit()

    def deposit(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self.save()

    def withdraw(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        self.save()

    def transfer(self, amount: float, target: "Account") -> None:
        with self._db.get_session() as session:
            try:
                self.withdraw(amount)
                target.deposit(amount)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e

    @classmethod
    def get_by_id(cls, id: str) -> Optional["Account"]:
        db = DatabaseConnection()
        with db.get_session() as session:
            db_account = session.query(AccountModel).filter_by(id=id).first()
            return cls.from_orm(db_account) if db_account else None

    @classmethod
    def get_by_name(cls, name: str) -> Optional["Account"]:
        db = DatabaseConnection()
        with db.get_session() as session:
            db_account = session.query(AccountModel).filter_by(name=name).first()
            return cls.from_orm(db_account) if db_account else None

    def __repr__(self) -> str:
        return f"Account(name='{self.name}', balance={self.balance:.2f})"

    def __str__(self) -> str:
        return f"{self.name} - {self.balance:.2f}"


class AccountManager:
    def __init__(self):
        self._db = DatabaseConnection()

    def get_account(self, name: str) -> Optional[Account]:
        return Account.get_by_name(name)

    def get_all_accounts(self) -> List[Account]:
        with self._db.get_session() as session:
            db_accounts = session.query(AccountModel).all()
            return [Account.from_orm(acc) for acc in db_accounts]

    def add_account(self, name: str, initial_balance: float = 0) -> None:
        if self.get_account(name):
            raise ValueError(f"Account '{name}' already exists")

        account = Account(name, initial_balance)
        try:
            account.save()
        except IntegrityError:
            raise ValueError(f"Account '{name}' already exists")

    def display_accounts(self) -> None:
        accounts = self.get_all_accounts()
        for account in accounts:
            print(f"{account.name} - Balance: {account.balance:.2f} DA")

    def edit_account(
        self, name: str, new_name: Optional[str], new_balance: Optional[float]
    ) -> None:
        with self._db.get_session() as session:
            account = self.get_account(name)
            if not account:
                raise ValueError(f"Account '{name}' not found")

            if new_name:
                account.name = new_name
            if new_balance is not None:
                account.balance = float(new_balance)

            try:
                account.save()
                print(f"Account '{name}' edited successfully.")
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Account name '{new_name}' already exists")

    def delete_account(self, name: str) -> None:
        with self._db.get_session() as session:
            db_account = session.query(AccountModel).filter_by(name=name).first()
            if not db_account:
                raise ValueError(f"Account '{name}' not found")

            session.delete(db_account)
            session.commit()
            print(f"Account '{name}' deleted successfully.")

    def transfer_between_accounts(
        self, from_account_name: str, to_account_name: str, amount: float
    ) -> None:
        with self._db.get_session() as session:
            try:
                from_account = self.get_account(from_account_name)
                if not from_account:
                    raise ValueError(f"Account '{from_account_name}' not found")

                to_account = self.get_account(to_account_name)
                if not to_account:
                    raise ValueError(f"Account '{to_account_name}' not found")

                from_account.transfer(amount, to_account)
                print(
                    f"{amount:.2f} DA transferred from '{from_account_name}' to '{to_account_name}'."
                )
            except Exception as e:
                session.rollback()
                raise e
