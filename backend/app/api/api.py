# fortuna/backend/app/api/api.py
from fastapi import APIRouter
from .v1 import accounts_router, categories_router, expense_router, income_router, subscriptions_router, transactions_router

api_router = APIRouter()

api_router.include_router(accounts_router, prefix="/accounts", tags=["accounts"])

api_router.include_router(categories_router, prefix="/categories", tags=["categories"])

api_router.include_router(expense_router, prefix="/expenses", tags=["expenses"])

api_router.include_router(income_router, prefix="/incomes", tags=["incomes"])

api_router.include_router(subscriptions_router, prefix="/subscriptions", tags=["subscriptions"])

api_router.include_router(transactions_router, prefix="/transactions", tags=["transactions"])
