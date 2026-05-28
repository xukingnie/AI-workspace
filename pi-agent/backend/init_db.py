"""初始化数据库：建表 + 种子数据"""
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


def init_database():
    """建表并插入默认分类"""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 如果分类表已有数据则跳过
        if db.query(Category).count() > 0:
            print("分类数据已存在，跳过种子数据插入")
            return

        for cat in DEFAULT_CATEGORIES:
            db.add(Category(**cat))

        db.commit()
        print(f"已插入 {len(DEFAULT_CATEGORIES)} 条默认分类")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
