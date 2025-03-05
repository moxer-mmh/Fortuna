# app/api/v1//transaction.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.db import get_db
from app.schemas import TransactionCreate, TransactionUpdate, Transaction
from app.services import TransactionService

router = APIRouter()


@router.post("/", response_model=Transaction)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    transaction_service = TransactionService(db)
    try:
        return transaction_service.create_transaction(transaction)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Transaction])
def get_all_transactions(
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[str] = None,
    account_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    subscription_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    transaction_service = TransactionService(db)
    # Here we would add filtering logic based on the query parameters
    # This would require modifications to the service layer
    return transaction_service.get_all_transactions()


@router.get("/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    transaction_service = TransactionService(db)
    transaction = transaction_service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: str, transaction: TransactionUpdate, db: Session = Depends(get_db)):
    transaction_service = TransactionService(db)
    try:
        updated_transaction = transaction_service.update_transaction(transaction_id, transaction)
        if not updated_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return updated_transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{transaction_id}", response_model=dict)
def delete_transaction(transaction_id: str, db: Session = Depends(get_db)):
    transaction_service = TransactionService(db)
    try:
        transaction_service.delete_transaction(transaction_id)
        return {"message": "Transaction deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


