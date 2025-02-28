# fortuna/backend/app/services/subscription_service.py
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from schemas import (
    SubscriptionCreate,
    SubscriptionUpdate,
    Subscription,
)
from schemas import Transaction
from db import (
    Subscription as SubscriptionModel,
    Transaction as TransactionModel,
    Category as CategoryModel,
    Account as AccountModel,
)


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db

    def create_subscription(
        self, subscription_data: SubscriptionCreate
    ) -> Subscription:
        # Validate that the expense category exists (subscriptions use expense categories)
        category = (
            self.db.query(CategoryModel)
            .filter(
                CategoryModel.id == subscription_data.category_id,
                CategoryModel.type == "expense",
            )
            .first()
        )
        if not category:
            raise HTTPException(
                status_code=404, detail="Expense category for subscription not found"
            )

        # Validate that the account exists
        account = (
            self.db.query(AccountModel)
            .filter(AccountModel.id == subscription_data.account_id)
            .first()
        )
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        subscription_dict = subscription_data.model_dump(exclude_unset=True)
        subscription = SubscriptionModel(**subscription_dict)
        self.db.add(subscription)
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Error creating subscription: " + str(e)
            )
        self.db.refresh(subscription)
        return subscription

    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        return (
            self.db.query(SubscriptionModel)
            .filter(SubscriptionModel.id == subscription_id)
            .first()
        )

    def get_all_subscriptions(self) -> List[Subscription]:
        return self.db.query(SubscriptionModel).all()

    def get_subscription_transactions(self, subscription_id: str) -> List[Transaction]:
        return (
            self.db.query(TransactionModel)
            .filter(TransactionModel.subscription_id == subscription_id)
            .all()
        )

    def update_subscription(
        self, subscription_id: str, subscription_data: SubscriptionUpdate
    ) -> Subscription:
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        update_data = subscription_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(subscription, key, value)
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Error updating subscription: " + str(e)
            )
        self.db.refresh(subscription)
        return subscription

    def delete_subscription(
        self, subscription_id: str, delete_transactions: bool = False
    ) -> None:
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        try:
            if delete_transactions:
                # Delete all transactions linked to the subscription
                self.db.query(TransactionModel).filter(
                    TransactionModel.subscription_id == subscription_id
                ).delete()
            # Delete the subscription
            self.db.delete(subscription)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Error deleting subscription: " + str(e)
            )

    def process_payment(self, subscription: SubscriptionModel) -> Optional[Transaction]:
        now = datetime.now()
        if not subscription.active or now < subscription.next_payment:
            return None

        # Validate associated account and category exist
        account = (
            self.db.query(AccountModel)
            .filter(AccountModel.id == subscription.account_id)
            .first()
        )
        if not account:
            raise HTTPException(
                status_code=404, detail="Account not found for subscription"
            )

        category = (
            self.db.query(CategoryModel)
            .filter(CategoryModel.id == subscription.category_id)
            .first()
        )
        if not category:
            raise HTTPException(
                status_code=404, detail="Category not found for subscription"
            )

        # Optionally, you might check the category budget here (skipped for brevity)

        # Create a new transaction for the subscription payment
        transaction = TransactionModel(
            date=subscription.next_payment,
            amount=subscription.amount,
            description=f"Subscription payment - {subscription.name}",
            account_id=subscription.account_id,
            category_id=subscription.category_id,
            type="subscription",
            subscription_id=subscription.id,
        )
        self.db.add(transaction)

        # Deduct the subscription amount from the account balance
        account.balance -= subscription.amount

        # Update the subscription's next payment date based on its frequency
        if subscription.frequency == "weekly":
            subscription.next_payment += timedelta(days=7)
        elif subscription.frequency == "monthly":
            month = subscription.next_payment.month
            year = subscription.next_payment.year
            if month == 12:
                subscription.next_payment = subscription.next_payment.replace(
                    year=year + 1, month=1
                )
            else:
                subscription.next_payment = subscription.next_payment.replace(
                    month=month + 1
                )
        elif subscription.frequency == "yearly":
            subscription.next_payment = subscription.next_payment.replace(
                year=subscription.next_payment.year + 1
            )

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Error processing subscription payment: " + str(e),
            )
        self.db.refresh(transaction)
        return transaction

    def process_due_payments(self) -> List[Transaction]:
        now = datetime.now()
        due_subscriptions = (
            self.db.query(SubscriptionModel)
            .filter(
                SubscriptionModel.active == True, SubscriptionModel.next_payment <= now
            )
            .all()
        )
        processed_transactions = []
        for sub in due_subscriptions:
            tx = self.process_payment(sub)
            if tx:
                processed_transactions.append(tx)
        return processed_transactions
