# finance_manager/database/models.py
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from .connection import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    balance = Column(Float, nullable=False)

    # Relationships
    transactions = relationship("Transaction", back_populates="account")
    subscriptions = relationship("Subscription", back_populates="account")


class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    budget = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # 'expense' or 'income'

    # Relationships
    transactions = relationship("Transaction", back_populates="category")
    subscriptions = relationship("Subscription", back_populates="category")


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


# Initialize database
def init_database():
    from .connection import DatabaseConnection

    db = DatabaseConnection()
    db.create_tables()
