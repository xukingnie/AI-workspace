"""初始化数据库：建表 + 种子数据"""
from sqlalchemy import inspect, text

from database import engine, SessionLocal, Base
from models import Category

DEFAULT_CATEGORIES = [
    # 支出分类
    {"name": "餐饮", "type": "expense", "icon": "food", "sort_order": 1},
    {"name": "交通", "type": "expense", "icon": "traffic", "sort_order": 2},
    {"name": "购物", "type": "expense", "icon": "shopping", "sort_order": 3},
    {"name": "娱乐", "type": "expense", "icon": "entertainment", "sort_order": 4},
    {"name": "居住", "type": "expense", "icon": "house", "sort_order": 5},
    {"name": "通讯", "type": "expense", "icon": "phone", "sort_order": 6},
    {"name": "医疗", "type": "expense", "icon": "medical", "sort_order": 7},
    {"name": "教育", "type": "expense", "icon": "education", "sort_order": 8},
    {"name": "其他支出", "type": "expense", "icon": "other-expense", "sort_order": 99},
    # 收入分类
    {"name": "工资", "type": "income", "icon": "salary", "sort_order": 1},
    {"name": "奖金", "type": "income", "icon": "bonus", "sort_order": 2},
    {"name": "投资收益", "type": "income", "icon": "investment", "sort_order": 3},
    {"name": "兼职", "type": "income", "icon": "parttime", "sort_order": 4},
    {"name": "其他收入", "type": "income", "icon": "other-income", "sort_order": 99},
]


def _ensure_legacy_columns():
    """兼容旧库结构：补齐 users 表关联列。"""
    inspector = inspect(engine)

    if "users" not in inspector.get_table_names():
        return

    category_columns = {col["name"] for col in inspector.get_columns("categories")}
    transaction_columns = {col["name"] for col in inspector.get_columns("transactions")}

    with engine.begin() as conn:
        if "user_id" not in category_columns:
            conn.execute(text("ALTER TABLE categories ADD COLUMN user_id INTEGER"))
        if "user_id" not in transaction_columns:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN user_id INTEGER"))


def init_database():
    """建表并兼容旧库结构。"""
    Base.metadata.create_all(bind=engine)
    _ensure_legacy_columns()

    db = SessionLocal()
    try:
        print(f"当前分类数量: {db.query(Category).count()}，等待用户首次登录后初始化专属分类")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
