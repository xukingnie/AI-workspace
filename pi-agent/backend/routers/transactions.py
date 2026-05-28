"""账单 CRUD 路由"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Transaction
from schemas import TransactionCreate, TransactionUpdate, TransactionOut

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
