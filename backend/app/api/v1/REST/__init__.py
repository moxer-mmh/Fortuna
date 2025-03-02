# fortuna/backend/app/api/v1/REST/__init__.py
from .accounts import router as accounts_router
from .categories import router as categories_router
from .expense import router as expense_router

__all__ = ["accounts_router", "categories_router", "expense_router"]
