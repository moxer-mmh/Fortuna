# fortuna/backend/app/services/transaction_service.py
from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas import (
    TransactionCreate,
    TransactionUpdate,
    Transaction,
)
from db import Transaction as TransactionModel


class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, transaction: TransactionCreate) -> Transaction:
        db_transaction = TransactionModel(**transaction.model_dump())
        self.db.add(db_transaction)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Error creating transaction")
        self.db.refresh(db_transaction)
        return db_transaction

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        return (
            self.db.query(TransactionModel)
            .filter(TransactionModel.id == transaction_id)
            .first()
        )

    def update_transaction(
        self, transaction_id: str, transaction: TransactionUpdate
    ) -> Optional[Transaction]:
        db_transaction = self.get_transaction(transaction_id)
        if not db_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        update_data = transaction.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_transaction, key, value)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction

    def delete_transaction(self, transaction_id: str) -> None:
        db_transaction = self.get_transaction(transaction_id)
        if not db_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        self.db.delete(db_transaction)
        self.db.commit()
