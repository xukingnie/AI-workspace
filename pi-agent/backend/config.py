"""数据库配置"""
import os

# 允许通过 DATABASE_URL 直接覆盖完整连接串
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
	# 默认使用 SQLite，开箱即用；如需 MySQL，设置 DB_DIALECT=mysql
	DB_DIALECT = os.getenv("DB_DIALECT", "sqlite").lower()

	if DB_DIALECT == "mysql":
		DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
		DB_PORT = int(os.getenv("DB_PORT", "3306"))
		DB_USER = os.getenv("DB_USER", "root")
		DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
		DB_NAME = os.getenv("DB_NAME", "accounting")
		DATABASE_URL = (
			f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
		)
	else:
		SQLITE_PATH = os.getenv("SQLITE_PATH", "./accounting.db")
		DATABASE_URL = f"sqlite:///{SQLITE_PATH}"


# 鉴权配置
APP_ENV = os.getenv("APP_ENV", "dev")
SECRET_KEY = os.getenv("SECRET_KEY", "pi-agent-dev-secret-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "30"))
SMS_CODE_TTL_SECONDS = int(os.getenv("SMS_CODE_TTL_SECONDS", "300"))
