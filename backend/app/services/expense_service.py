#fortuna/backend/app/services/expense_service.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from db import Transaction as TransactionModel
from db import Category as CategoryModel
from db import Account as AccountModel
from db import DatabaseConnection
from .transaction_service import Transaction
from .category_service import Category
from .account_service import Account


class Expense:
    def __init__(self, transaction: Transaction, category: Category, account: Account):
        if not transaction:
            raise ValueError("Transaction cannot be None")
        if not category:
            raise ValueError("Category cannot be None")
        if not account:
            raise ValueError("Account cannot be None")

        self.transaction = transaction
        self.category = category
        self.account = account
        self._db = DatabaseConnection()

        self.transaction.type = "expense"
        self.transaction.category_id = category.id

    def save(self) -> bool:
        with self._db.get_session() as session:
            if not self._validate_category_budget(session):
                print(
                    f"Budget limit reached for category: {self.category.name} this month"
                )
                print("Do you want to continue?")
                if input("y/n: ").lower() != "y":
                    return False

            try:
                # Begin transaction
                self.transaction.save()

                # Update account balance
                db_account = (
                    session.query(AccountModel).filter_by(id=self.account.id).first()
                )
                if not db_account:
                    raise ValueError(f"Account with id {self.account.id} not found")

                db_account.balance -= self.transaction.amount
                session.commit()
                return True

            except Exception as e:
                session.rollback()
                print(f"Error saving expense: {str(e)}")
                return False

    def delete(self) -> None:
        with self._db.get_session() as session:
            try:
                # Begin transaction
                db_transaction = (
                    session.query(TransactionModel)
                    .filter_by(id=self.transaction.id)
                    .first()
                )
                if not db_transaction:
                    raise ValueError(
                        f"Transaction with id {self.transaction.id} not found"
                    )

                # Update account balance
                db_account = (
                    session.query(AccountModel).filter_by(id=self.account.id).first()
                )
                if not db_account:
                    raise ValueError(f"Account with id {self.account.id} not found")

                db_account.balance += db_transaction.amount
                session.delete(db_transaction)
                session.commit()

            except Exception as e:
                session.rollback()
                print(f"Error deleting expense: {str(e)}")

    def _validate_category_budget(self, session: Session) -> bool:
        if not self.category.can_add_transaction(
            self.transaction.amount, self.transaction.date
        ):
            return False
        return True

    @classmethod
    def add_expense(
        cls,
        date: datetime,
        amount: float,
        description: str,
        category: Category,
        account: Account,
    ) -> Optional["Expense"]:
        transaction = Transaction(
            date=date,
            amount=amount,
            description=description,
            account_id=account.id,
            category_id=category.id,
            type="expense",
        )
        expense = cls(transaction, category, account)
        if expense.save():
            return expense
        return None

    @classmethod
    def get_by_id(cls, transaction_id: str) -> Optional["Expense"]:
        db = DatabaseConnection()
        with db.get_session() as session:
            db_transaction = (
                session.query(TransactionModel)
                .filter_by(id=transaction_id, type="expense")
                .first()
            )

            if not db_transaction:
                return None

            db_category = (
                session.query(CategoryModel)
                .filter_by(id=db_transaction.category_id)
                .first()
            )
            db_account = (
                session.query(AccountModel)
                .filter_by(id=db_transaction.account_id)
                .first()
            )

            if not db_category or not db_account:
                return None

            transaction = Transaction.from_orm(db_transaction)
            category = Category.from_orm(db_category)
            account = Account.from_orm(db_account)

            return cls(transaction, category, account)

    @classmethod
    def get_all_expenses(cls) -> List["Expense"]:
        db = DatabaseConnection()
        expenses = []

        with db.get_session() as session:
            db_transactions = (
                session.query(TransactionModel).filter_by(type="expense").all()
            )

            for db_transaction in db_transactions:
                try:
                    db_category = (
                        session.query(CategoryModel)
                        .filter_by(id=db_transaction.category_id)
                        .first()
                    )
                    db_account = (
                        session.query(AccountModel)
                        .filter_by(id=db_transaction.account_id)
                        .first()
                    )

                    if not db_category or not db_account:
                        continue

                    transaction = Transaction.from_orm(db_transaction)
                    category = Category.from_orm(db_category)
                    account = Account.from_orm(db_account)

                    expense = cls(transaction, category, account)
                    expenses.append(expense)

                except Exception as e:
                    print(f"Error processing transaction {db_transaction.id}: {str(e)}")
                    continue

        return expenses

    def __str__(self) -> str:
        return (
            f"Expense: {self.transaction} - Description: {self.transaction.description} "
            f"- Category: {self.category.name} - Account: {self.account.name}"
        )


class ExpenseManager:
    def __init__(self):
        self._db = DatabaseConnection()

    def add_expense(
        self,
        account_manager,
        date_str: str,
        amount: float,
        description: str,
        category_name: str,
        account_name: str,
    ) -> Optional[Expense]:
        with self._db.get_session() as session:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")

                # Get category
                db_category = (
                    session.query(CategoryModel)
                    .filter_by(name=category_name, type="expense")
                    .first()
                )
                if not db_category:
                    raise ValueError(f"Category '{category_name}' not found")
                category = Category.from_orm(db_category)

                # Get account
                account = account_manager.get_account(account_name)
                if not account:
                    raise ValueError(f"Account '{account_name}' not found")

                expense = Expense.add_expense(
                    date, amount, description, category, account
                )
                if expense:
                    print("Expense added successfully.")
                    return expense
                else:
                    print("Failed to add expense.")
                    return None

            except ValueError as e:
                print(f"Error: {str(e)}")
                return None
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                return None

    def add_category(self, name: str, budget: float) -> None:
        with self._db.get_session() as session:
            try:
                # Check if category already exists
                existing_category = (
                    session.query(CategoryModel)
                    .filter_by(name=name, type="expense")
                    .first()
                )
                if existing_category:
                    raise ValueError(f"Category '{name}' already exists")

                # Create new category
                category = Category(name=name, budget=budget, type="expense")
                category.save()
                print("Category added successfully.")

            except Exception as e:
                print(f"Error adding category: {str(e)}")

    def get_expense(self, transaction_id: str) -> Optional[Expense]:
        return Expense.get_by_id(transaction_id)

    def get_category(self, name: str) -> Optional[Category]:
        with self._db.get_session() as session:
            db_category = (
                session.query(CategoryModel)
                .filter_by(name=name, type="expense")
                .first()
            )
            return Category.from_orm(db_category) if db_category else None

    def get_all_categories(self) -> List[Category]:
        with self._db.get_session() as session:
            db_categories = session.query(CategoryModel).filter_by(type="expense").all()
            return [Category.from_orm(cat) for cat in db_categories]

    def get_all_expenses(self) -> List[Expense]:
        return Expense.get_all_expenses()

    def display_expenses(self) -> None:
        try:
            expenses = self.get_all_expenses()
            if not expenses:
                print("No expenses found.")
                return

            print("\nExpense List:")
            print("-" * 80)
            for expense in expenses:
                try:
                    print(expense)
                except Exception as e:
                    print(f"Error displaying expense: {str(e)}")
            print("-" * 80)

        except Exception as e:
            print(f"Error retrieving expenses: {str(e)}")

    def display_categories(self) -> None:
        categories = self.get_all_categories()
        for category in categories:
            print(f"{category.name} (Budget: {category.budget:.2f} DA)")

    def edit_expense(
        self,
        expense_id: str,
        new_date_str: Optional[str],
        new_amount_str: Optional[str],
        new_description: Optional[str],
        new_category_name: Optional[str],
    ) -> None:
        with self._db.get_session() as session:
            try:
                expense = self.get_expense(expense_id)
                if not expense:
                    print("Expense not found.")
                    return

                # Revert the account balance
                db_account = (
                    session.query(AccountModel).filter_by(id=expense.account.id).first()
                )
                if not db_account:
                    raise ValueError("Account not found")
                db_account.balance += expense.transaction.amount

                # Update transaction details
                if new_date_str:
                    expense.transaction.date = datetime.strptime(
                        new_date_str, "%Y-%m-%d"
                    )
                if new_amount_str:
                    expense.transaction.amount = float(new_amount_str)
                if new_description:
                    expense.transaction.description = new_description
                if new_category_name:
                    new_category = self.get_category(new_category_name)
                    if not new_category:
                        print("Category not found.")
                        session.rollback()
                        return
                    expense.category = new_category
                    expense.transaction.category_id = new_category.id

                # Save changes
                if expense.save():
                    print("Expense edited successfully.")
                else:
                    print("Failed to edit expense.")
                    session.rollback()

            except Exception as e:
                session.rollback()
                print(f"Error editing expense: {str(e)}")

    def edit_category(
        self, category_name: str, new_name: Optional[str], new_budget: Optional[float]
    ) -> None:
        with self._db.get_session() as session:
            try:
                db_category = (
                    session.query(CategoryModel)
                    .filter_by(name=category_name, type="expense")
                    .first()
                )
                if not db_category:
                    print("Category not found.")
                    return

                if new_name:
                    db_category.name = new_name
                if new_budget is not None:
                    db_category.budget = new_budget

                session.commit()
                print("Category edited successfully.")

            except Exception as e:
                session.rollback()
                print(f"Error editing category: {str(e)}")

    def delete_expense(self, expense_id: str) -> None:
        expense = self.get_expense(expense_id)
        if not expense:
            print("Expense not found.")
            return

        expense.delete()
        print("Expense deleted successfully.")

    def delete_category(self, category_name: str) -> None:
        with self._db.get_session() as session:
            try:
                # Get category
                db_category = (
                    session.query(CategoryModel)
                    .filter_by(name=category_name, type="expense")
                    .first()
                )
                if not db_category:
                    print("Category not found.")
                    return

                # Delete all associated expenses
                db_transactions = (
                    session.query(TransactionModel)
                    .filter_by(category_id=db_category.id, type="expense")
                    .all()
                )

                for db_transaction in db_transactions:
                    # Update account balance
                    db_account = (
                        session.query(AccountModel)
                        .filter_by(id=db_transaction.account_id)
                        .first()
                    )
                    if db_account:
                        db_account.balance += db_transaction.amount
                    session.delete(db_transaction)

                # Delete category
                session.delete(db_category)
                session.commit()
                print("Category deleted successfully.")

            except Exception as e:
                session.rollback()
                print(f"Error deleting category: {str(e)}")
