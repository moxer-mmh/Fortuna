# app/api/v1/subscription.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.schemas import SubscriptionCreate, SubscriptionUpdate, Subscription, Transaction
from app.services import SubscriptionService

router = APIRouter()


@router.post("/", response_model=Subscription)
def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    subscription_service = SubscriptionService(db)
    try:
        return subscription_service.create_subscription(subscription)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Subscription])
def get_all_subscriptions(db: Session = Depends(get_db), active_only: bool = False):
    subscription_service = SubscriptionService(db)
    subscriptions = subscription_service.get_all_subscriptions()
    if active_only:
        subscriptions = [sub for sub in subscriptions if sub.active]
    return subscriptions


@router.get("/{subscription_id}", response_model=Subscription)
def get_subscription(subscription_id: str, db: Session = Depends(get_db)):
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.put("/{subscription_id}", response_model=Subscription)
def update_subscription(subscription_id: str, subscription: SubscriptionUpdate, db: Session = Depends(get_db)):
    subscription_service = SubscriptionService(db)
    try:
        updated_subscription = subscription_service.update_subscription(subscription_id, subscription)
        if not updated_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return updated_subscription
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{subscription_id}", response_model=dict)
def delete_subscription(subscription_id: str, delete_transactions: bool = False, db: Session = Depends(get_db)):
    subscription_service = SubscriptionService(db)
    try:
        subscription_service.delete_subscription(subscription_id, delete_transactions)
        return {"message": "Subscription deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{subscription_id}/transactions", response_model=List[Transaction])
def get_subscription_transactions(subscription_id: str, db: Session = Depends(get_db)):
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription_service.get_subscription_transactions(subscription_id)


@router.post("/process-due", response_model=List[Transaction])
def process_due_payments(db: Session = Depends(get_db)):
    subscription_service = SubscriptionService(db)
    try:
        processed = subscription_service.process_due_payments()
        return processed
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


