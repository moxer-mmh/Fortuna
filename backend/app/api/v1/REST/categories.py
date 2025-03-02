# app/api/v1/category.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.schemas import CategoryCreate, CategoryUpdate, Category
from app.services import CategoryService

router = APIRouter()


@router.post("/", response_model=Category)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    category_service = CategoryService(db)
    try:
        return category_service.create_category(category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Category])
def get_all_categories(db: Session = Depends(get_db), type: str = None):
    category_service = CategoryService(db)
    categories = category_service.get_all_categories()
    if type:
        categories = [cat for cat in categories if cat.type.lower() == type.lower()]
    return categories


@router.get("/{category_id}", response_model=Category)
def get_category(category_id: str, db: Session = Depends(get_db)):
    category_service = CategoryService(db)
    category = category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: str, category: CategoryUpdate, db: Session = Depends(get_db)
):
    category_service = CategoryService(db)
    try:
        updated_category = category_service.update_category(category_id, category)
        if not updated_category:
            raise HTTPException(status_code=404, detail="Category not found")
        return updated_category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", response_model=dict)
def delete_category(category_id: str, db: Session = Depends(get_db)):
    category_service = CategoryService(db)
    try:
        category_service.delete_category(category_id)
        return {"message": "Category deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
