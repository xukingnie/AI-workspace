"""Pydantic 请求/响应模型"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


# ==================== 分类 ====================

class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=50)
    type: str = Field(..., pattern="^(income|expense)$")
    icon: str = Field(default="")
    sort_order: int = Field(default=0)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    icon: Optional[str] = None
    sort_order: Optional[int] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    type: str
    icon: str
    sort_order: int

    model_config = {"from_attributes": True}


# ==================== 账单 ====================

class TransactionCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    type: str = Field(..., pattern="^(income|expense)$")
    category_id: int
    transaction_date: date
    note: str = Field(default="")


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    category_id: Optional[int] = None
    transaction_date: Optional[date] = None
    note: Optional[str] = None


class TransactionOut(BaseModel):
    id: int
    amount: Decimal
    type: str
    category_id: int
    transaction_date: date
    note: str
    created_at: datetime
    category: Optional[CategoryOut] = None

    model_config = {"from_attributes": True}


class NoteSuggestionOut(BaseModel):
    note: str
    count: int
    last_used_at: datetime


class AmountSuggestionOut(BaseModel):
    amount: Decimal
    count: int
    last_used_at: datetime


# ==================== 统计 ====================

class OverviewOut(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal


class CategoryStatOut(BaseModel):
    category_id: int
    category_name: str
    category_icon: str
    total: Decimal
    percentage: float


class DailyStatOut(BaseModel):
    date: date
    income: Decimal
    expense: Decimal


# ==================== 用户/鉴权 ====================

class SendCodeIn(BaseModel):
    phone: str = Field(..., pattern="^1[3-9]\\d{9}$")


class SendCodeOut(BaseModel):
    message: str
    expire_seconds: int
    debug_code: Optional[str] = None


class LoginByCodeIn(BaseModel):
    phone: str = Field(..., pattern="^1[3-9]\\d{9}$")
    code: str = Field(..., min_length=4, max_length=8)


class UserOut(BaseModel):
    id: int
    phone: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthTokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut
