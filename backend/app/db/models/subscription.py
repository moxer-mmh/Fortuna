#fortuna/backend/app/db/models/subscription.py
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from ..session import Base
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    frequency = Column(String, nullable=False)
    next_payment = Column(DateTime, nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    # Foreign Keys
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)

    # Relationships
    category = relationship("Category", back_populates="subscriptions")
    account = relationship("Account", back_populates="subscriptions")
    transactions = relationship("Transaction", back_populates="subscription")