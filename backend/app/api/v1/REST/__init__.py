#fortuna/backend/app/api/v1/REST/__init__.py
from .accounts import router as accounts_router
from .expense import router as expense_router
__all__ = ["accounts_router","expense_router"]
