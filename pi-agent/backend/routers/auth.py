"""用户鉴权路由。"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config import ACCESS_TOKEN_EXPIRE_DAYS, SMS_CODE_TTL_SECONDS
from database import get_db
from dependencies import get_current_user
from models import Category, Transaction, User
from schemas import AuthTokenOut, LoginByCodeIn, SendCodeIn, SendCodeOut, UserOut
from services.auth_service import (
    create_access_token,
    generate_sms_code,
    get_send_code_debug_value,
    verify_sms_code,
)

router = APIRouter(prefix="/api/auth", tags=["用户鉴权"])

DEFAULT_CATEGORIES = [
    {"name": "餐饮", "type": "expense", "icon": "food", "sort_order": 1},
    {"name": "交通", "type": "expense", "icon": "traffic", "sort_order": 2},
    {"name": "购物", "type": "expense", "icon": "shopping", "sort_order": 3},
    {"name": "娱乐", "type": "expense", "icon": "entertainment", "sort_order": 4},
    {"name": "居住", "type": "expense", "icon": "house", "sort_order": 5},
    {"name": "通讯", "type": "expense", "icon": "phone", "sort_order": 6},
    {"name": "医疗", "type": "expense", "icon": "medical", "sort_order": 7},
    {"name": "教育", "type": "expense", "icon": "education", "sort_order": 8},
    {"name": "其他支出", "type": "expense", "icon": "other-expense", "sort_order": 99},
    {"name": "工资", "type": "income", "icon": "salary", "sort_order": 1},
    {"name": "奖金", "type": "income", "icon": "bonus", "sort_order": 2},
    {"name": "投资收益", "type": "income", "icon": "investment", "sort_order": 3},
    {"name": "兼职", "type": "income", "icon": "parttime", "sort_order": 4},
    {"name": "其他收入", "type": "income", "icon": "other-income", "sort_order": 99},
]


def _bootstrap_user_data(db: Session, user: User):
    """首个登录用户继承历史数据，其他用户初始化默认分类。"""
    user_count = db.query(User).count()

    if user_count == 1:
        db.query(Category).filter(Category.user_id.is_(None)).update(
            {Category.user_id: user.id}, synchronize_session=False
        )
        db.query(Transaction).filter(Transaction.user_id.is_(None)).update(
            {Transaction.user_id: user.id}, synchronize_session=False
        )
        db.commit()

    has_category = db.query(Category).filter(Category.user_id == user.id).first()
    if has_category:
        return

    for cat in DEFAULT_CATEGORIES:
        db.add(Category(user_id=user.id, **cat))
    db.commit()


@router.post("/send-code", response_model=SendCodeOut)
def send_code(data: SendCodeIn):
    code = generate_sms_code(data.phone)
    return SendCodeOut(
        message="验证码已发送",
        expire_seconds=SMS_CODE_TTL_SECONDS,
        debug_code=get_send_code_debug_value(code),
    )


@router.post("/login-by-code", response_model=AuthTokenOut)
def login_by_code(data: LoginByCodeIn, db: Session = Depends(get_db)):
    if not verify_sms_code(data.phone, data.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已过期")

    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        user = User(phone=data.phone)
        db.add(user)
        db.commit()
        db.refresh(user)

    _bootstrap_user_data(db, user)

    token = create_access_token(user.id, user.phone)
    return AuthTokenOut(
        access_token=token,
        expires_in=ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout():
    return {"message": "退出成功"}
