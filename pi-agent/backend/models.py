"""ORM 模型定义"""
from datetime import datetime
from sqlalchemy import String, Integer, DECIMAL, Date, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="分类名称")
    type: Mapped[str] = mapped_column(
        Enum("income", "expense", name="category_type"),
        nullable=False,
        comment="收入/支出",
    )
    icon: Mapped[str] = mapped_column(String(50), default="", comment="图标标识")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )

    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    amount: Mapped[float] = mapped_column(
        DECIMAL(10, 2), nullable=False, comment="金额"
    )
    type: Mapped[str] = mapped_column(
        Enum("income", "expense", name="transaction_type"),
        nullable=False,
        comment="收入/支出",
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=False, comment="分类ID"
    )
    transaction_date: Mapped[datetime] = mapped_column(
        Date, nullable=False, comment="交易日期"
    )
    note: Mapped[str] = mapped_column(String(200), default="", comment="备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )

    category = relationship("Category", back_populates="transactions")
