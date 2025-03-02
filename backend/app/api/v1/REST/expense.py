from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.db import get_db
from app.schemas import ExpenseCreate, ExpenseUpdate, Expense
from app.services import ExpenseService

router = APIRouter()


@router.post("/", response_model=Expense)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    expense_service = ExpenseService(db)
    try:
        return expense_service.create_expense(expense)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Expense])
def get_all_expenses(
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[str] = None,
    account_id: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    expense_service = ExpenseService(db)
    # Here we would add filtering logic based on the query parameters
    # For now, we just return all expenses
    return expense_service.get_all_expenses()


@router.get("/{expense_id}", response_model=Expense)
def get_expense(expense_id: str, db: Session = Depends(get_db)):
    expense_service = ExpenseService(db)
    expense = expense_service.get_expense(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/{expense_id}", response_model=Expense)
def update_expense(
    expense_id: str, expense: ExpenseUpdate, db: Session = Depends(get_db)
):
    expense_service = ExpenseService(db)
    try:
        updated_expense = expense_service.update_expense(expense_id, expense)
        if not updated_expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        return updated_expense
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{expense_id}", response_model=dict)
def delete_expense(expense_id: str, db: Session = Depends(get_db)):
    expense_service = ExpenseService(db)
    try:
        expense_service.delete_expense(expense_id)
        return {"message": "Expense deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
