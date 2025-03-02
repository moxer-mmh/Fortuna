# fortuna/backend/app/services/account_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from ..schemas import Account, AccountCreate, AccountUpdate, AccountTransfer
from ..db import Account as AccountModel


class AccountService:
    def __init__(self, db: Session):
        self.db = db

    def create_account(self, account: AccountCreate) -> Account:
        # Convert the Pydantic model to a dict and pass it to the ORM model
        db_account = AccountModel(**account.model_dump())
        self.db.add(db_account)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Account already exists")
        self.db.refresh(db_account)
        return db_account

    def get_account(self, account_id: str) -> Optional[Account]:
        db_account = (
            self.db.query(AccountModel).filter(AccountModel.id == account_id).first()
        )
        return db_account

    def get_all_accounts(self) -> List[Account]:
        db_accounts = self.db.query(AccountModel).all()
        return db_accounts

    def update_account(
        self, account_id: str, account: AccountUpdate
    ) -> Optional[Account]:
        db_account = self.get_account(account_id)
        if not db_account:
            raise HTTPException(status_code=404, detail="Account not found")
        # Only update provided fields
        update_data = account.model_dump(exclude_unset=True)
        allowed_fields = ["name", "balance"]
        update_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        for key, value in update_data.items():
            setattr(db_account, key, value)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account

    def delete_account(self, account_id: str) -> None:
        db_account = self.get_account(account_id)
        if not db_account:
            raise HTTPException(status_code=404, detail="Account not found")
        self.db.delete(db_account)
        self.db.commit()
        return True

    def transfer_between_accounts(self, transfer_data: AccountTransfer) -> None:
        sender_account = self.get_account(transfer_data.from_account_id)
        receiver_account = self.get_account(transfer_data.to_account_id)
        if not sender_account or not receiver_account:
            raise HTTPException(status_code=404, detail="Account not found")
        sender_account.balance -= transfer_data.amount
        receiver_account.balance += transfer_data.amount
        self.db.commit()
        return True
