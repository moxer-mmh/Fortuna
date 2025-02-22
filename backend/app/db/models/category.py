#fortuna/backend/app/db/models/category.py
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from ..session import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    budget = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # 'expense' or 'income'

    # Relationships
    transactions = relationship("Transaction", back_populates="category")
    subscriptions = relationship("Subscription", back_populates="category")