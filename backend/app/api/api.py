# fortuna/backend/app/api/api.py
from fastapi import APIRouter
from .v1 import accounts_router

api_router = APIRouter()

api_router.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
