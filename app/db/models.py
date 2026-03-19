from sqlalchemy import (
    Column, Integer, String, Float,
    DateTime, ForeignKey, Text, create_engine
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Month(Base):
    __tablename__ = "months"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    month       = Column(Integer, nullable=False)   # 1-12
    year        = Column(Integer, nullable=False)   # e.g. 2025
    label       = Column(String, nullable=False)    # e.g. "Sep 2025"
    file_name   = Column(String)                    # original filename
    imported_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship(
        "Transaction", back_populates="month_ref",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f""


class Transaction(Base):
    __tablename__ = "transactions"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    month_id            = Column(Integer, ForeignKey("months.id"), nullable=False)
    date                = Column(String, nullable=False)   # "01-09-2025"
    year                = Column(String)
    description         = Column(Text)
    mode_of_transaction = Column(String)
    paid_to             = Column(String)
    debit               = Column(Float, default=0.0)
    credit              = Column(Float, default=0.0)
    balance             = Column(Float, default=0.0)
    category            = Column(String)

    month_ref = relationship("Month", back_populates="transactions")

    def __repr__(self):
        return f""


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    role       = Column(String, nullable=False)   # "user" or "assistant"
    message    = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f""