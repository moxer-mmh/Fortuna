from datetime import datetime
from typing import List, Optional
from ..database import Transaction as TransactionModel
from ..database import Category as CategoryModel
from ..database import Account as AccountModel
from ..database import DatabaseConnection
from .transaction import Transaction
from .category import Category
from .account import Account


class Income:
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

        self.transaction.type = "income"
        self.transaction.category_id = category.id

    def save(self) -> bool:
        with self._db.get_session() as session:
            try:
                # Begin transaction
                self.transaction.save()

                # Update account balance
                db_account = (
                    session.query(AccountModel).filter_by(id=self.account.id).first()
                )
                if not db_account:
                    raise ValueError(f"Account with id {self.account.id} not found")

                db_account.balance += self.transaction.amount
                session.commit()
                return True

            except Exception as e:
                session.rollback()
                print(f"Error saving income: {str(e)}")
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

                db_account.balance -= db_transaction.amount
                session.delete(db_transaction)
                session.commit()

            except Exception as e:
                session.rollback()
                print(f"Error deleting income: {str(e)}")

    @classmethod
    def add_income(
        cls,
        date: datetime,
        amount: float,
        description: str,
        category: Category,
        account: Account,
    ) -> Optional["Income"]:
        transaction = Transaction(
            date=date,
            amount=amount,
            description=description,
            account_id=account.id,
            category_id=category.id,
            type="income",
        )
        income = cls(transaction, category, account)
        if income.save():
            return income
        return None

    @classmethod
    def get_by_id(cls, transaction_id: str) -> Optional["Income"]:
        db = DatabaseConnection()
        with db.get_session() as session:
            db_transaction = (
                session.query(TransactionModel)
                .filter_by(id=transaction_id, type="income")
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
    def get_all_incomes(cls) -> List["Income"]:
        db = DatabaseConnection()
        incomes = []

        with db.get_session() as session:
            db_transactions = (
                session.query(TransactionModel).filter_by(type="income").all()
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

                    income = cls(transaction, category, account)
                    incomes.append(income)

                except Exception as e:
                    print(f"Error processing transaction {db_transaction.id}: {str(e)}")
                    continue

        return incomes

    def __str__(self) -> str:
        return (
            f"Income: {self.transaction} - Description: {self.transaction.description} "
            f"- Category: {self.category.name} - Account: {self.account.name}"
        )


class IncomeManager:
    def __init__(self):
        self._db = DatabaseConnection()

    def add_income(
        self,
        account_manager,
        date_str: str,
        amount: float,
        description: str,
        category_name: str,
        account_name: str,
    ) -> Optional[Income]:
        with self._db.get_session() as session:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")

                # Get category
                db_category = (
                    session.query(CategoryModel)
                    .filter_by(name=category_name, type="income")
                    .first()
                )
                if not db_category:
                    raise ValueError(f"Category '{category_name}' not found")
                category = Category.from_orm(db_category)

                # Get account
                account = account_manager.get_account(account_name)
                if not account:
                    raise ValueError(f"Account '{account_name}' not found")

                income = Income.add_income(date, amount, description, category, account)
                if income:
                    print("Income added successfully.")
                    return income
                else:
                    print("Failed to add income.")
                    return None

            except ValueError as e:
                print(f"Error: {str(e)}")
                return None
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                return None

    def add_category(self, name: str, target: float) -> None:
        with self._db.get_session() as session:
            try:
                # Check if category already exists
                existing_category = (
                    session.query(CategoryModel)
                    .filter_by(name=name, type="income")
                    .first()
                )
                if existing_category:
                    raise ValueError(f"Category '{name}' already exists")

                # Create new category
                category = Category(name=name, budget=target, type="income")
                category.save()
                print("Category added successfully.")

            except Exception as e:
                print(f"Error adding category: {str(e)}")

    def get_income(self, transaction_id: str) -> Optional[Income]:
        return Income.get_by_id(transaction_id)

    def get_category(self, name: str) -> Optional[Category]:
        with self._db.get_session() as session:
            db_category = (
                session.query(CategoryModel).filter_by(name=name, type="income").first()
            )
            return Category.from_orm(db_category) if db_category else None

    def get_all_categories(self) -> List[Category]:
        with self._db.get_session() as session:
            db_categories = session.query(CategoryModel).filter_by(type="income").all()
            return [Category.from_orm(cat) for cat in db_categories]

    def get_all_incomes(self) -> List[Income]:
        return Income.get_all_incomes()

    def display_incomes(self) -> None:
        try:
            incomes = self.get_all_incomes()
            if not incomes:
                print("No incomes found.")
                return

            print("\nIncome List:")
            print("-" * 80)
            for income in incomes:
                try:
                    print(income)
                except Exception as e:
                    print(f"Error displaying income: {str(e)}")
            print("-" * 80)

        except Exception as e:
            print(f"Error retrieving incomes: {str(e)}")

    def display_categories(self) -> None:
        categories = self.get_all_categories()
        for category in categories:
            print(f"{category.name} (Target: {category.budget:.2f} DA)")

    def edit_income(
        self,
        income_id: str,
        new_date_str: Optional[str],
        new_amount_str: Optional[str],
        new_description: Optional[str],
        new_category_name: Optional[str],
    ) -> None:
        with self._db.get_session() as session:
            try:
                income = self.get_income(income_id)
                if not income:
                    print("Income not found.")
                    return

                # Revert the account balance
                db_account = (
                    session.query(AccountModel).filter_by(id=income.account.id).first()
                )
                if not db_account:
                    raise ValueError("Account not found")
                db_account.balance -= income.transaction.amount

                # Update transaction details
                if new_date_str:
                    income.transaction.date = datetime.strptime(
                        new_date_str, "%Y-%m-%d"
                    )
                if new_amount_str:
                    income.transaction.amount = float(new_amount_str)
                if new_description:
                    income.transaction.description = new_description
                if new_category_name:
                    new_category = self.get_category(new_category_name)
                    if not new_category:
                        print("Category not found.")
                        session.rollback()
                        return
                    income.category = new_category
                    income.transaction.category_id = new_category.id

                # Save changes
                if income.save():
                    print("Income edited successfully.")
                else:
                    print("Failed to edit income.")
                    session.rollback()

            except Exception as e:
                session.rollback()
                print(f"Error editing income: {str(e)}")

    def edit_category(
        self, category_name: str, new_name: Optional[str], new_target: Optional[float]
    ) -> None:
        with self._db.get_session() as session:
            try:
                db_category = (
                    session.query(CategoryModel)
                    .filter_by(name=category_name, type="income")
                    .first()
                )
                if not db_category:
                    print("Category not found.")
                    return

                if new_name:
                    db_category.name = new_name
                if new_target is not None:
                    db_category.budget = new_target

                session.commit()
                print("Category edited successfully.")

            except Exception as e:
                session.rollback()
                print(f"Error editing category: {str(e)}")

    def delete_income(self, income_id: str) -> None:
        income = self.get_income(income_id)
        if not income:
            print("Income not found.")
            return

        income.delete()
        print("Income deleted successfully.")

    def delete_category(self, category_name: str) -> None:
        with self._db.get_session() as session:
            try:
                # Get category
                db_category = (
                    session.query(CategoryModel)
                    .filter_by(name=category_name, type="income")
                    .first()
                )
                if not db_category:
                    print("Category not found.")
                    return

                # Delete all associated incomes
                db_transactions = (
                    session.query(TransactionModel)
                    .filter_by(category_id=db_category.id, type="income")
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
                        db_account.balance -= db_transaction.amount
                    session.delete(db_transaction)

                # Delete category
                session.delete(db_category)
                session.commit()
                print("Category deleted successfully.")

            except Exception as e:
                session.rollback()
                print(f"Error deleting category: {str(e)}")
