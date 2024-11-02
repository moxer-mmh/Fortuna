from datetime import datetime
from typing import Optional
import uuid
from ..database import Transaction as TransactionModel
from ..database import DatabaseConnection


class Transaction:
    def __init__(
        self,
        date: datetime,
        amount: float,
        description: str,
        account_id: str,
        category_id: str = None,
        type: str = None,
        id: str = None,
        subscription_id: str = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.date = (
            date if isinstance(date, datetime) else datetime.strptime(date, "%Y-%m-%d")
        )
        self.amount = amount
        self.description = description
        self.account_id = account_id
        self.category_id = category_id
        self.type = type
        self.subscription_id = subscription_id
        self._db = DatabaseConnection()

    @classmethod
    def from_orm(cls, db_transaction: TransactionModel) -> "Transaction":
        """Convert ORM model instance to Transaction domain object"""
        return cls(
            date=db_transaction.date,
            amount=db_transaction.amount,
            description=db_transaction.description,
            account_id=db_transaction.account_id,
            category_id=db_transaction.category_id,
            type=db_transaction.type,
            id=db_transaction.id,
            subscription_id=db_transaction.subscription_id,
        )

    def to_orm(self) -> TransactionModel:
        """Convert Transaction domain object to ORM model instance"""
        return TransactionModel(
            id=self.id,
            date=self.date,
            amount=self.amount,
            description=self.description,
            account_id=self.account_id,
            category_id=self.category_id,
            type=self.type,
            subscription_id=self.subscription_id,
        )

    def save(self) -> None:
        with self._db.get_session() as session:
            db_transaction = (
                session.query(TransactionModel).filter_by(id=self.id).first()
            )
            if db_transaction:
                db_transaction.date = self.date
                db_transaction.amount = self.amount
                db_transaction.description = self.description
                db_transaction.account_id = self.account_id
                db_transaction.category_id = self.category_id
                db_transaction.type = self.type
                db_transaction.subscription_id = self.subscription_id
            else:
                db_transaction = self.to_orm()
                session.add(db_transaction)
            session.commit()

    @classmethod
    def get_by_id(cls, id: str) -> Optional["Transaction"]:
        db = DatabaseConnection()
        with db.get_session() as session:
            db_transaction = session.query(TransactionModel).filter_by(id=id).first()
            return cls.from_orm(db_transaction) if db_transaction else None

    def delete(self) -> None:
        with self._db.get_session() as session:
            db_transaction = (
                session.query(TransactionModel).filter_by(id=self.id).first()
            )
            if db_transaction:
                session.delete(db_transaction)
                session.commit()

    def __str__(self) -> str:
        return f"(id='{self.id}' - date='{self.date.strftime('%Y-%m-%d')}' - amount={self.amount:.2f})"

    def __repr__(self) -> str:
        return self.__str__()
