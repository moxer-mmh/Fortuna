from typing import List, Optional
from datetime import datetime, timedelta
from .transaction import Transaction
from .category import Category
from .account import Account
from ..database import DatabaseConnection
import uuid


class Subscription:
    def __init__(
        self,
        name: str,
        amount: float,
        frequency: str,
        category: Category,
        account: Account,
        next_payment: datetime = None,
        active: bool = True,
        id: str = None,
    ):
        if not category or category.type != "expense":
            raise ValueError("Category must be an expense category")
        if not account:
            raise ValueError("Account cannot be None")

        self.id = id or str(uuid.uuid4())
        self.name = name
        self.amount = amount
        self.frequency = frequency
        self.category = category
        self.account = account
        self.next_payment = next_payment or datetime.now()
        self.active = active
        self.db = DatabaseConnection()

    def save(self):
        self.db.execute_query(
            """
            INSERT OR REPLACE INTO subscriptions 
            (id, name, amount, frequency, next_payment, category_id, account_id, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.id,
                self.name,
                self.amount,
                self.frequency,
                self.next_payment.strftime("%Y-%m-%d"),
                self.category.id,
                self.account.id,
                self.active,
            ),
        )

    def delete(self):
        self.db.execute_query("DELETE FROM subscriptions WHERE id = ?", (self.id,))

    def process_payment(self) -> Optional[Transaction]:
        if not self.active or datetime.now() < self.next_payment:
            return None
        if not self.category.can_add_transaction(self.amount, self.next_payment):
            print(f"Budget limit reached for category: {self.category.name} this month")
            print("Do you want to continue?")
            if input("y/n: ").lower() != "y":
                return None
            else:
                transaction = Transaction(
                    date=self.next_payment,
                    amount=self.amount,
                    description=f"Subscription payment - {self.name}",
                    account_id=self.account.id,
                    category_id=self.category.id,
                    type="subscription",
                    subscription_id=self.id,
                )

                transaction.save()
                self.account.withdraw(self.amount)

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

                self.save()
                return transaction
        else:
            transaction = Transaction(
                date=self.next_payment,
                amount=self.amount,
                description=f"Subscription payment - {self.name}",
                account_id=self.account.id,
                category_id=self.category.id,
                type="subscription",
                subscription_id=self.id,
            )

            transaction.save()
            self.account.withdraw(self.amount)

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

            self.save()
            return transaction

    @classmethod
    def get_by_id(cls, id: str) -> Optional["Subscription"]:
        db = DatabaseConnection()
        result = db.fetch_one(
            """
            SELECT id, name, amount, frequency, next_payment, category_id, account_id, active
            FROM subscriptions
            WHERE id = ?
            """,
            (id,),
        )

        if result:
            category = Category.get_by_id(result[5])
            account = Account.get_by_id(result[6])
            return cls(
                name=result[1],
                amount=result[2],
                frequency=result[3],
                next_payment=datetime.strptime(result[4], "%Y-%m-%d"),
                category=category,
                account=account,
                active=result[7],
                id=result[0],
            )
        return None

    def get_transactions(self) -> List[Transaction]:
        results = self.db.fetch_all(
            """
            SELECT id, date, amount, description, account_id, category_id, type, subscription_id
            FROM transactions
            WHERE subscription_id = ?
            ORDER BY date DESC
            """,
            (self.id,),
        )

        return [
            Transaction(
                date=row[1],
                amount=row[2],
                description=row[3],
                account_id=row[4],
                category_id=row[5],
                type=row[6],
                id=row[0],
                subscription_id=row[7],
            )
            for row in results
        ]

    def __str__(self):
        status = "Active" if self.active else "Inactive"
        return (
            f"Subscription: {self.name} - Amount: {self.amount:.2f} - Frequency: {self.frequency} - "
            f"Next payment: {self.next_payment.strftime('%Y-%m-%d')} - Status: {status}"
        )


class SubscriptionManager:
    def __init__(self):
        self.db = DatabaseConnection()

    def add_subscription(
        self,
        expense_manager,
        account_manager,
        name,
        amount,
        frequency,
        category_name,
        account_name,
        next_payment_str,
    ) -> Optional[Subscription]:
        try:

            category = expense_manager.get_category(category_name)
            if not category:
                raise ValueError(f"Category '{category_name}' not found")

            account = account_manager.get_account(account_name)
            if not account:
                raise ValueError(f"Account '{account_name}' not found")

            next_payment = datetime.strptime(next_payment_str, "%Y-%m-%d")

            subscription = Subscription(
                name=name,
                amount=amount,
                frequency=frequency,
                category=category,
                account=account,
                next_payment=next_payment,
            )
            subscription.save()
            print("Subscription added successfully.")
            return subscription
        except ValueError as e:
            print(f"Error: {str(e)}")
            return None

    def get_subscription(self, id: str) -> Optional[Subscription]:
        return Subscription.get_by_id(id)

    def get_all_subscriptions(self) -> List[Subscription]:
        results = self.db.fetch_all(
            """
            SELECT id, name, amount, frequency, next_payment, category_id, account_id, active
            FROM subscriptions
            """
        )

        subscriptions = []
        for row in results:
            try:
                category = Category.get_by_id(row[5])
                account = Account.get_by_id(row[6])

                subscription = Subscription(
                    name=row[1],
                    amount=row[2],
                    frequency=row[3],
                    next_payment=datetime.strptime(row[4], "%Y-%m-%d"),
                    category=category,
                    account=account,
                    active=row[7],
                    id=row[0],
                )
                subscriptions.append(subscription)
            except Exception as e:
                print(f"Error processing subscription {row[0]}: {str(e)}")
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

    def display_subscriptions_transactions(self, subscription_id) -> None:

        if subscription_id:
            subscription = self.get_subscription(subscription_id)
            if not subscription:
                print(f"No subscription found with ID: {subscription_id}")
                return

            transactions = subscription.get_transactions()
            print(f"\nTransactions for subscription: {subscription.name}")
        else:
            results = self.db.fetch_all(
                """
                SELECT t.id, t.date, t.amount, t.description, t.account_id, 
                    t.category_id, t.type, t.subscription_id, s.name
                FROM transactions t
                JOIN subscriptions s ON t.subscription_id = s.id
                WHERE t.type = 'subscription'
                ORDER BY t.date DESC
                """
            )

            transactions = []
            for row in results:
                transaction = Transaction(
                    date=row[1],
                    amount=row[2],
                    description=row[3],
                    account_id=row[4],
                    category_id=row[5],
                    type=row[6],
                    id=row[0],
                    subscription_id=row[7],
                )
                transactions.append((transaction, row[8]))

        if not transactions:
            print("No transactions found.")
            return

        print("\nTransaction List:")
        print("-" * 100)

        if subscription_id:
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
            t.amount if subscription_id else t[0].amount for t in transactions
        )
        transaction_count = len(transactions)
        print(f"\nSummary:")
        print(f"Total Transactions: {transaction_count}")
        print(f"Total Amount: ${total_amount:.2f}")

    def edit_subscription(
        self,
        subscription_id,
        new_name,
        new_amount_str,
        new_frequency,
        new_category_name,
        new_account_name,
        new_next_payment_str,
        new_active_str,
    ) -> None:
        try:
            self.display_subscriptions()
            subscription = self.get_subscription(subscription_id)

            if not subscription:
                print("Subscription not found.")
                return

            print("\nCurrent subscription details:")
            print(subscription)
            print("\nLeave fields blank to keep current values.")

            if new_name:
                subscription.name = new_name

            if new_amount_str:
                try:
                    new_amount = float(new_amount_str)
                    if new_amount <= 0:
                        raise ValueError("Amount must be positive")
                    subscription.amount = new_amount
                except ValueError as e:
                    print(f"Invalid amount: {str(e)}")
                    return

            if new_frequency:
                if new_frequency not in ["weekly", "monthly", "yearly"]:
                    print("Invalid frequency. Must be weekly, monthly, or yearly.")
                    return
                subscription.frequency = new_frequency

            if new_category_name:
                new_category = Category.get_by_name(new_category_name, "expense")
                if not new_category:
                    print(f"Category '{new_category_name}' not found.")
                    return
                subscription.category = new_category

            if new_account_name:
                new_account = Account.get_by_name(new_account_name)
                if not new_account:
                    print(f"Account '{new_account_name}' not found.")
                    return
                subscription.account = new_account

            if new_next_payment_str:
                try:
                    new_next_payment = datetime.strptime(
                        new_next_payment_str, "%Y-%m-%d"
                    )
                    subscription.next_payment = new_next_payment
                except ValueError:
                    print("Invalid date format. Use YYYY-MM-DD.")
                    return

            if new_active_str:
                if new_active_str == "active":
                    subscription.active = True
                elif new_active_str == "inactive":
                    subscription.active = False
                else:
                    print("Invalid status. Must be 'active' or 'inactive'.")
                    return

            subscription.save()
            print("\nSubscription updated successfully:")
            print(subscription)

        except Exception as e:
            print(f"Error editing subscription: {str(e)}")

    def delete_subscription(self, subscription_id) -> None:
        try:
            self.display_subscriptions()
            subscription = self.get_subscription(subscription_id)

            if not subscription:
                print("Subscription not found.")
                return

            print("\nCurrent subscription details:")
            print(subscription)

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
                    self.db.execute_query(
                        "UPDATE transactions SET subscription_id = NULL WHERE subscription_id = ?",
                        (subscription.id,),
                    )
                    subscription.delete()
                    print("Subscription deleted. Transactions have been kept.")

                elif choice == "2":
                    for transaction in transactions:
                        subscription.account.deposit(transaction.amount)
                        transaction.delete()
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
            print(f"Error deleting subscription: {str(e)}")
