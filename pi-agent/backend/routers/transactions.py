"""账单 CRUD 路由"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Transaction
from schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionOut,
    NoteSuggestionOut,
    AmountSuggestionOut,
)

router = APIRouter(prefix="/api/transactions", tags=["账单"])


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    type: str | None = Query(None, pattern="^(income|expense)$"),
    category_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """查询账单列表，支持筛选和分页"""
    q = db.query(Transaction).options(joinedload(Transaction.category))

    if type:
        q = q.filter(Transaction.type == type)
    if category_id:
        q = q.filter(Transaction.category_id == category_id)
    if start_date:
        q = q.filter(Transaction.transaction_date >= start_date)
    if end_date:
        q = q.filter(Transaction.transaction_date <= end_date)

    total = q.count()
    items = (
        q.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # 附加 total 到响应头（简化做法）
    return items


@router.post("", response_model=TransactionOut)
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db)):
    """新增账单"""
    txn = Transaction(**data.model_dump())
    db.add(txn)
    db.commit()
    # 重新查询加载关联的 category
    txn = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(Transaction.id == txn.id)
        .first()
    )
    return txn


@router.get("/note-suggestions", response_model=list[NoteSuggestionOut])
def list_note_suggestions(
    category_id: int | None = Query(None, ge=1),
    type: str | None = Query(None, pattern="^(income|expense)$"),
    limit: int = Query(8, ge=1, le=20),
    recent_days: int = Query(30, ge=1, le=3650),
    db: Session = Depends(get_db),
):
    """按分类返回常用备注建议（最近优先，去重）"""
    if not category_id:
        return []

    window_start = date.fromordinal(date.today().toordinal() - recent_days)

    q = (
        db.query(
            func.trim(Transaction.note).label("note"),
            func.count(Transaction.id).label("count"),
            func.max(Transaction.created_at).label("last_used_at"),
        )
        .filter(Transaction.category_id == category_id)
        .filter(Transaction.transaction_date >= window_start)
        .filter(Transaction.note.isnot(None))
        .filter(func.trim(Transaction.note) != "")
    )

    if type:
        q = q.filter(Transaction.type == type)

    rows = (
        q.group_by(func.trim(Transaction.note))
        .order_by(func.max(Transaction.created_at).desc(), func.count(Transaction.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "note": row.note,
            "count": int(row.count),
            "last_used_at": row.last_used_at,
        }
        for row in rows
        if row.last_used_at is not None
    ]


@router.get("/amount-suggestions", response_model=list[AmountSuggestionOut])
def list_amount_suggestions(
    category_id: int | None = Query(None, ge=1),
    type: str | None = Query(None, pattern="^(income|expense)$"),
    limit: int = Query(8, ge=1, le=20),
    recent_days: int = Query(30, ge=1, le=3650),
    db: Session = Depends(get_db),
):
    """按分类返回常用金额建议（最近优先，去重）"""
    if not category_id:
        return []

    window_start = date.fromordinal(date.today().toordinal() - recent_days)

    q = (
        db.query(
            Transaction.amount.label("amount"),
            func.count(Transaction.id).label("count"),
            func.max(Transaction.created_at).label("last_used_at"),
        )
        .filter(Transaction.category_id == category_id)
        .filter(Transaction.transaction_date >= window_start)
        .filter(Transaction.amount > 0)
    )

    if type:
        q = q.filter(Transaction.type == type)

    rows = (
        q.group_by(Transaction.amount)
        .order_by(func.max(Transaction.created_at).desc(), func.count(Transaction.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "amount": row.amount,
            "count": int(row.count),
            "last_used_at": row.last_used_at,
        }
        for row in rows
        if row.last_used_at is not None
    ]


@router.get("/amount-by-note", response_model=AmountSuggestionOut | None)
def get_amount_by_note(
    category_id: int = Query(..., ge=1),
    note: str = Query(..., min_length=1, max_length=200),
    type: str | None = Query(None, pattern="^(income|expense)$"),
    recent_days: int = Query(90, ge=1, le=3650),
    db: Session = Depends(get_db),
):
    """按分类+备注返回联动金额建议（最近优先）"""
    normalized_note = note.strip()
    if not normalized_note:
        return None

    window_start = date.fromordinal(date.today().toordinal() - recent_days)

    row = (
        db.query(
            Transaction.amount.label("amount"),
            func.count(Transaction.id).label("count"),
            func.max(Transaction.created_at).label("last_used_at"),
        )
        .filter(Transaction.category_id == category_id)
        .filter(Transaction.transaction_date >= window_start)
        .filter(func.trim(Transaction.note) == normalized_note)
        .filter(Transaction.amount > 0)
        .filter(Transaction.note.isnot(None))
    )

    if type:
        row = row.filter(Transaction.type == type)

    row = (
        row.group_by(Transaction.amount)
        .order_by(func.max(Transaction.created_at).desc(), func.count(Transaction.id).desc())
        .first()
    )

    if not row or row.last_used_at is None:
        return None

    return {
        "amount": row.amount,
        "count": int(row.count),
        "last_used_at": row.last_used_at,
    }


@router.put("/{txn_id}", response_model=TransactionOut)
def update_transaction(txn_id: int, data: TransactionUpdate, db: Session = Depends(get_db)):
    """编辑账单"""
    txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="账单不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(txn, key, val)
    db.commit()
    txn = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(Transaction.id == txn.id)
        .first()
    )
    return txn


@router.delete("/{txn_id}")
def delete_transaction(txn_id: int, db: Session = Depends(get_db)):
    """删除账单"""
    txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="账单不存在")
    db.delete(txn)
    db.commit()
    return {"message": "删除成功"}
