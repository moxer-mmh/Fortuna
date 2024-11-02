from datetime import datetime, timedelta
from typing import List, Optional
from ..database import Transaction as TransactionModel
from ..database import Category as CategoryModel
from ..database import Account as AccountModel
from ..database import Subscription as SubscriptionModel
from ..database import DatabaseConnection
from .transaction import Transaction
from .category import Category
from .account import Account


class Subscription:
    def __init__(self, model: SubscriptionModel, category: Category, account: Account):
        if not model:
            raise ValueError("Subscription model cannot be None")
        if not category or category.type != "expense":
            raise ValueError("Category must be an expense category")
        if not account:
            raise ValueError("Account cannot be None")

        self.model = model
        self.category = category
        self.account = account
        self._db = DatabaseConnection()

    @property
    def id(self) -> str:
        return self.model.id

    @property
    def name(self) -> str:
        return self.model.name

    @name.setter
    def name(self, value: str):
        self.model.name = value

    @property
    def amount(self) -> float:
        return self.model.amount

    @amount.setter
    def amount(self, value: float):
        self.model.amount = value

    @property
    def frequency(self) -> str:
        return self.model.frequency

    @frequency.setter
    def frequency(self, value: str):
        self.model.frequency = value

    @property
    def next_payment(self) -> datetime:
        return self.model.next_payment

    @next_payment.setter
    def next_payment(self, value: datetime):
        self.model.next_payment = value

    @property
    def active(self) -> bool:
        return self.model.active

    @active.setter
    def active(self, value: bool):
        self.model.active = value

    def save(self) -> bool:
        with self._db.get_session() as session:
            try:
                session.add(self.model)
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                print(f"Error saving subscription: {str(e)}")
                return False

    def delete(self) -> None:
        with self._db.get_session() as session:
            try:
                session.delete(self.model)
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"Error deleting subscription: {str(e)}")

    def process_payment(self) -> Optional[Transaction]:
        if not self.active or datetime.now() < self.next_payment:
            return None

        with self._db.get_session() as session:
            if not self.category.can_add_transaction(self.amount, self.next_payment):
                print(
                    f"Budget limit reached for category: {self.category.name} this month"
                )
                print("Do you want to continue?")
                if input("y/n: ").lower() != "y":
                    return None

            try:
                # Create transaction
                transaction_model = TransactionModel(
                    date=self.next_payment,
                    amount=self.amount,
                    description=f"Subscription payment - {self.name}",
                    account_id=self.account.id,
                    category_id=self.category.id,
                    type="subscription",
                    subscription_id=self.id,
                )

                # Update account balance
                db_account = (
                    session.query(AccountModel).filter_by(id=self.account.id).first()
                )
                if not db_account:
                    raise ValueError(f"Account with id {self.account.id} not found")
                db_account.balance -= self.amount

                # Update next payment date
                if self.frequency == "weekly":
                    self.next_payment += timedelta(days=7)
                elif self.frequency == "monthly":
                    if self.next_payment.month == 12:
                        self.next_payment = self.next_payment.replace(
                            year=self.next_payment.year + 1, month=1
                        )
                    else:
                        self.next_payment = self.next_payment.replace(
                            month=self.next_payment.month + 1
                        )
                elif self.frequency == "yearly":
                    self.next_payment = self.next_payment.replace(
                        year=self.next_payment.year + 1
                    )

                session.add(transaction_model)
                session.add(self.model)
                session.commit()

                return Transaction.from_orm(transaction_model)

            except Exception as e:
                session.rollback()
                print(f"Error processing payment: {str(e)}")
                return None

    def get_transactions(self) -> List[Transaction]:
        with self._db.get_session() as session:
            db_transactions = (
                session.query(TransactionModel)
                .filter_by(subscription_id=self.id)
                .order_by(TransactionModel.date.desc())
                .all()
            )
            return [Transaction.from_orm(t) for t in db_transactions]

    @classmethod
    def create(
        cls,
        name: str,
        amount: float,
        frequency: str,
        category: Category,
        account: Account,
        next_payment: datetime = None,
        active: bool = True,
    ) -> "Subscription":
        model = SubscriptionModel(
            name=name,
            amount=amount,
            frequency=frequency,
            category_id=category.id,
            account_id=account.id,
            next_payment=next_payment or datetime.now(),
            active=active,
        )
        return cls(model, category, account)

    @classmethod
    def get_by_id(cls, subscription_id: str) -> Optional["Subscription"]:
        db = DatabaseConnection()
        with db.get_session() as session:
            db_subscription = (
                session.query(SubscriptionModel).filter_by(id=subscription_id).first()
            )
            if not db_subscription:
                return None

            db_category = (
                session.query(CategoryModel)
                .filter_by(id=db_subscription.category_id)
                .first()
            )
            db_account = (
                session.query(AccountModel)
                .filter_by(id=db_subscription.account_id)
                .first()
            )

            if not db_category or not db_account:
                return None

            category = Category.from_orm(db_category)
            account = Account.from_orm(db_account)

            return cls(db_subscription, category, account)

    def __str__(self) -> str:
        status = "Active" if self.active else "Inactive"
        return (
            f"Subscription: {self.name} - Amount: {self.amount:.2f} - Frequency: {self.frequency} - "
            f"Next payment: {self.next_payment.strftime('%Y-%m-%d')} - Status: {status}"
        )


class SubscriptionManager:
    def __init__(self):
        self._db = DatabaseConnection()

    def add_subscription(
        self,
        expense_manager,
        account_manager,
        name: str,
        amount: float,
        frequency: str,
        category_name: str,
        account_name: str,
        next_payment_str: str,
    ) -> Optional[Subscription]:
        with self._db.get_session() as session:
            try:
                category = expense_manager.get_category(category_name)
                if not category:
                    raise ValueError(f"Category '{category_name}' not found")

                account = account_manager.get_account(account_name)
                if not account:
                    raise ValueError(f"Account '{account_name}' not found")

                next_payment = datetime.strptime(next_payment_str, "%Y-%m-%d")

                subscription = Subscription.create(
                    name=name,
                    amount=amount,
                    frequency=frequency,
                    category=category,
                    account=account,
                    next_payment=next_payment,
                )

                if subscription.save():
                    print("Subscription added successfully.")
                    return subscription
                return None

            except ValueError as e:
                print(f"Error: {str(e)}")
                return None

    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        return Subscription.get_by_id(subscription_id)

    def get_all_subscriptions(self) -> List[Subscription]:
        with self._db.get_session() as session:
            db_subscriptions = session.query(SubscriptionModel).all()
            subscriptions = []

            for db_subscription in db_subscriptions:
                try:
                    db_category = (
                        session.query(CategoryModel)
                        .filter_by(id=db_subscription.category_id)
                        .first()
                    )
                    db_account = (
                        session.query(AccountModel)
                        .filter_by(id=db_subscription.account_id)
                        .first()
                    )

                    if not db_category or not db_account:
                        continue

                    category = Category.from_orm(db_category)
                    account = Account.from_orm(db_account)

                    subscription = Subscription(db_subscription, category, account)
                    subscriptions.append(subscription)

                except Exception as e:
                    print(
                        f"Error processing subscription {db_subscription.id}: {str(e)}"
                    )
                    continue

            return subscriptions

    def process_due_payments(self) -> List[Transaction]:
        subscriptions = self.get_all_subscriptions()
        processed_transactions = []

        for subscription in subscriptions:
            transaction = subscription.process_payment()
            if transaction:
                processed_transactions.append(transaction)

        return processed_transactions

    def display_subscriptions(self) -> None:
        subscriptions = self.get_all_subscriptions()
        if not subscriptions:
            print("No subscriptions found.")
            return

        print("\nSubscription List:")
        print("-" * 80)
        for subscription in subscriptions:
            print(subscription)
        print("-" * 80)

    def display_subscriptions_transactions(
        self, subscription_id: Optional[str]
    ) -> None:
        with self._db.get_session() as session:
            if subscription_id:
                subscription = self.get_subscription(subscription_id)
                if not subscription:
                    print(f"No subscription found with ID: {subscription_id}")
                    return

                transactions = subscription.get_transactions()
                print(f"\nTransactions for subscription: {subscription.name}")
                if not transactions:
                    print("No transactions found.")
                    return
                self._print_transaction_list(transactions, False)

            else:
                # Fetch all transactions tied to subscriptions
                transactions = (
                    session.query(TransactionModel)
                    .filter(TransactionModel.subscription_id.isnot(None))
                    .order_by(TransactionModel.date.desc())
                    .all()
                )

                # Retrieve subscription names for the transactions
                transactions_with_names = []
                for transaction in transactions:
                    subscription_name = (
                        session.query(SubscriptionModel.name)
                        .filter(SubscriptionModel.id == transaction.subscription_id)
                        .scalar()
                    )  # Get the name
                    transactions_with_names.append((transaction, subscription_name))

                transactions = transactions_with_names  # Store transactions with names
                if not transactions:
                    print("No transactions found.")
                    return
                self._print_transaction_list(transactions, True)

    def _print_transaction_list(
        self, transactions: List, include_subscription_name: bool
    ) -> None:
        print("\nTransaction List:")
        print("-" * 100)

        if not include_subscription_name:
            print(f"{'Date':<12} {'Amount':>10} {'Description':<50}")
            print("-" * 100)
            for transaction in transactions:
                date_str = transaction.date.strftime("%Y-%m-%d")
                print(
                    f"{date_str:<12} {transaction.amount:>10.2f} {transaction.description:<50}"
                )
        else:
            print(
                f"{'Date':<12} {'Amount':>10} {'Subscription':<20} {'Description':<50}"
            )
            print("-" * 100)
            for transaction, subscription_name in transactions:
                date_str = transaction.date.strftime("%Y-%m-%d")
                print(
                    f"{date_str:<12} {transaction.amount:>10.2f} {subscription_name:<20} {transaction.description:<50}"
                )

        print("-" * 100)

        total_amount = sum(
            t.amount if not include_subscription_name else t[0].amount
            for t in transactions
        )
        print(f"\nSummary:")
        print(f"Total Transactions: {len(transactions)}")
        print(f"Total Amount: ${total_amount:.2f}")

    def edit_subscription(
        self,
        subscription_id: str,
        new_name: Optional[str],
        new_amount_str: Optional[str],
        new_frequency: Optional[str],
        new_category_name: Optional[str],
        new_account_name: Optional[str],
        new_next_payment_str: Optional[str],
        new_active_str: Optional[str],
    ) -> None:
        with self._db.get_session() as session:
            try:
                # Retrieve the subscription model directly from the session
                db_subscription = (
                    session.query(SubscriptionModel)
                    .filter_by(id=subscription_id)
                    .first()
                )
                if not db_subscription:
                    print("Subscription not found.")
                    return

                # Update fields as needed
                if new_name:
                    db_subscription.name = new_name

                if new_amount_str:
                    try:
                        new_amount = float(new_amount_str)
                        if new_amount <= 0:
                            raise ValueError("Amount must be positive")
                        db_subscription.amount = new_amount
                    except ValueError as e:
                        print(f"Invalid amount: {str(e)}")
                        return

                if new_frequency:
                    if new_frequency not in ["weekly", "monthly", "yearly"]:
                        print("Invalid frequency. Must be weekly, monthly, or yearly.")
                        return
                    db_subscription.frequency = new_frequency

                if new_category_name:
                    new_category = Category.get_by_name(new_category_name, "expense")
                    if not new_category:
                        print(f"Category '{new_category_name}' not found.")
                        return
                    db_subscription.category_id = new_category.id

                if new_account_name:
                    new_account = Account.get_by_name(new_account_name)
                    if not new_account:
                        print(f"Account '{new_account_name}' not found.")
                        return
                    db_subscription.account_id = new_account.id

                if new_next_payment_str:
                    try:
                        new_next_payment = datetime.strptime(
                            new_next_payment_str, "%Y-%m-%d"
                        )
                        db_subscription.next_payment = new_next_payment
                    except ValueError:
                        print("Invalid date format. Use YYYY-MM-DD.")
                        return

                if new_active_str:
                    if new_active_str == "active":
                        db_subscription.active = True
                    elif new_active_str == "inactive":
                        db_subscription.active = False
                    else:
                        print("Invalid status. Must be 'active' or 'inactive'.")
                        return

                # Commit the changes
                session.commit()
                print("\nSubscription updated successfully:")

            except Exception as e:
                session.rollback()
                print(f"Error editing subscription: {str(e)}")

    def delete_subscription(self, subscription_id: str) -> None:
        with self._db.get_session() as session:
            try:
                subscription = self.get_subscription(subscription_id)
                if not subscription:
                    print("Subscription not found.")
                    return

                transactions = subscription.get_transactions()
                if transactions:
                    print(
                        f"\nThis subscription has {len(transactions)} associated transactions."
                    )
                    print("Options:")
                    print("1. Delete subscription and keep transactions")
                    print("2. Delete subscription and all associated transactions")
                    print("3. Cancel deletion")

                    choice = input("\nEnter your choice (1-3): ")

                    if choice == "1":
                        for transaction in transactions:
                            session.query(TransactionModel).filter_by(
                                id=transaction.id
                            ).update({"subscription_id": None, "type": "expense"})
                        subscription.delete()
                        print("Subscription deleted. Transactions have been kept.")

                    elif choice == "2":
                        for transaction in transactions:
                            subscription.account.deposit(transaction.amount)
                            session.query(TransactionModel).filter_by(
                                id=transaction.id
                            ).delete()
                        subscription.delete()
                        print(
                            "Subscription and all associated transactions have been deleted."
                        )

                    elif choice == "3":
                        print("Deletion cancelled.")
                        return

                    else:
                        print("Invalid choice. Deletion cancelled.")
                        return

                else:
                    confirm = input(
                        "\nAre you sure you want to delete this subscription? (yes/no): "
                    )
                    if confirm.lower() == "yes":
                        subscription.delete()
                        print("Subscription deleted successfully.")
                    else:
                        print("Deletion cancelled.")

            except Exception as e:
                session.rollback()
                print(f"Error deleting subscription: {str(e)}")
