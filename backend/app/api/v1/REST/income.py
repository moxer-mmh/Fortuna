# app/api/v1/income.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.db import get_db
from app.schemas import IncomeCreate, IncomeUpdate, Income
from app.services import IncomeService

router = APIRouter()


@router.post("/", response_model=Income)
def create_income(income: IncomeCreate, db: Session = Depends(get_db)):
    income_service = IncomeService(db)
    try:
        return income_service.create_income(income)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Income])
def get_all_incomes(
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
    income_service = IncomeService(db)
    # Here we would add filtering logic based on the query parameters
    # For now, we just return all incomes
    return income_service.get_all_incomes()


@router.get("/{income_id}", response_model=Income)
def get_income(income_id: str, db: Session = Depends(get_db)):
    income_service = IncomeService(db)
    income = income_service.get_income(income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")
    return income


@router.put("/{income_id}", response_model=Income)
def update_income(income_id: str, income: IncomeUpdate, db: Session = Depends(get_db)):
    income_service = IncomeService(db)
    try:
        updated_income = income_service.update_income(income_id, income)
        if not updated_income:
            raise HTTPException(status_code=404, detail="Income not found")
        return updated_income
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{income_id}", response_model=dict)
def delete_income(income_id: str, db: Session = Depends(get_db)):
    income_service = IncomeService(db)
    try:
        income_service.delete_income(income_id)
        return {"message": "Income deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

