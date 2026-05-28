"""分类 CRUD 路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Category
from schemas import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter(prefix="/api/categories", tags=["分类"])


@router.get("", response_model=list[CategoryOut])
def list_categories(type: str | None = None, db: Session = Depends(get_db)):
    """获取分类列表，可按类型筛选"""
    q = db.query(Category)
    if type:
        q = q.filter(Category.type == type)
    return q.order_by(Category.sort_order).all()


@router.post("", response_model=CategoryOut)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    """新增分类"""
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/{cat_id}", response_model=CategoryOut)
def update_category(cat_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    """编辑分类"""
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(cat, key, val)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db)):
    """删除分类"""
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    db.delete(cat)
    db.commit()
    return {"message": "删除成功"}
