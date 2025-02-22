#fortuna/backend/app/db/models/transaction.py
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from ..session import Base
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    amount = Column(Float, nullable=False)
    description = Column(String)
    type = Column(String, nullable=False)  # 'expense', 'income', or 'subscription'

    # Foreign Keys
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscriptions.id"))

    # Relationships
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    subscription = relationship("Subscription", back_populates="transactions")