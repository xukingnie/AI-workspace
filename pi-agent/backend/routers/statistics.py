"""统计路由"""
from datetime import date
from decimal import Decimal
import calendar

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from database import get_db
from models import Transaction, Category
from schemas import OverviewOut, CategoryStatOut, DailyStatOut

router = APIRouter(prefix="/api/statistics", tags=["统计"])


def _month_range(year: int, month: int) -> tuple[date, date]:
    """返回指定年月的起止日期（含边界）"""
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


@router.get("/overview", response_model=OverviewOut)
def get_overview(
    year: int = Query(..., description="年份"),
    month: int = Query(..., ge=1, le=12, description="月份"),
    db: Session = Depends(get_db),
):
    """获取月度收支总览"""
    start_date, end_date = _month_range(year, month)

    income = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.type == "income",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
        )
        .scalar()
    )
    expense = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.type == "expense",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
        )
        .scalar()
    )
    return OverviewOut(
        total_income=Decimal(str(income)),
        total_expense=Decimal(str(expense)),
        balance=Decimal(str(income)) - Decimal(str(expense)),
    )


@router.get("/by-category", response_model=list[CategoryStatOut])
def get_by_category(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    type: str = Query(..., pattern="^(income|expense)$"),
    db: Session = Depends(get_db),
):
    """按分类统计指定月份的收支"""
    start_date, end_date = _month_range(year, month)

    rows = (
        db.query(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            Category.icon.label("category_icon"),
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Transaction.type == type,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
        )
        .group_by(Category.id)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    total = sum(Decimal(str(r.total)) for r in rows) if rows else Decimal("0")

    result = []
    for r in rows:
        pct = (
            float(Decimal(str(r.total)) / total * 100) if total > 0 else 0
        )
        result.append(
            CategoryStatOut(
                category_id=r.category_id,
                category_name=r.category_name,
                category_icon=r.category_icon,
                total=Decimal(str(r.total)),
                percentage=round(pct, 1),
            )
        )
    return result


@router.get("/daily", response_model=list[DailyStatOut])
def get_daily(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
):
    """获取指定月份每日收支汇总（日历用）"""
    start_date, end_date = _month_range(year, month)

    rows = (
        db.query(
            Transaction.transaction_date.label("date"),
            func.coalesce(
                func.sum(
                    case((Transaction.type == "income", Transaction.amount), else_=0)
                ),
                0,
            ).label("income"),
            func.coalesce(
                func.sum(
                    case((Transaction.type == "expense", Transaction.amount), else_=0)
                ),
                0,
            ).label("expense"),
        )
        .filter(
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
        )
        .group_by(Transaction.transaction_date)
        .all()
    )
    return [
        DailyStatOut(
            date=r.date,
            income=Decimal(str(r.income)),
            expense=Decimal(str(r.expense)),
        )
        for r in rows
    ]
