"""ORM 模型定义"""
from datetime import datetime
from sqlalchemy import String, Integer, DECIMAL, Date, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True, comment="所属用户ID"
    )
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

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, comment="手机号")
    password_hash: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="密码哈希（预留）"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    categories = relationship("Category", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


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
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True, comment="所属用户ID"
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

    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
