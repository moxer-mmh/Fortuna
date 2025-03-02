# app/api/v1/account.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.schemas import (
    AccountCreate,
    AccountUpdate,
    Account,
    AccountTransfer,
)
from app.services import AccountService

router = APIRouter()


@router.post("/", response_model=Account)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    account_service = AccountService(db)
    try:
        return account_service.create_account(account)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Account])
def get_all_accounts(db: Session = Depends(get_db)):
    account_service = AccountService(db)
    return account_service.get_all_accounts()


@router.get("/{account_id}", response_model=Account)
def get_account(account_id: str, db: Session = Depends(get_db)):
    account_service = AccountService(db)
    account = account_service.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/{account_id}", response_model=Account)
def update_account(
    account_id: str, account: AccountUpdate, db: Session = Depends(get_db)
):
    account_service = AccountService(db)
    try:
        updated_account = account_service.update_account(account_id, account)
        if not updated_account:
            raise HTTPException(status_code=404, detail="Account not found")
        return updated_account
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{account_id}", response_model=dict)
def delete_account(account_id: str, db: Session = Depends(get_db)):
    account_service = AccountService(db)
    try:
        account_service.delete_account(account_id)
        return {"message": "Account deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transfer", response_model=dict)
def transfer_between_accounts(transfer: AccountTransfer, db: Session = Depends(get_db)):
    account_service = AccountService(db)
    try:
        account_service.transfer_between_accounts(transfer)
        return {"message": "Transfer completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
