#fortuna/backend/app/db/models/account.py
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from ..session import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    balance = Column(Float, nullable=False)

    # Relationships
    transactions = relationship("Transaction", back_populates="account")
    subscriptions = relationship("Subscription", back_populates="account")