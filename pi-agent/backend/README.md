# backend

## Quick Start (uv + SQLite)

默认数据库已改为 SQLite，无需先安装 MySQL。

```powershell
cd D:/AI-workspace/pi-agent/backend
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
uv run python .\init_db.py
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

访问地址：

- API: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/docs

## Switch To MySQL (Optional)

```powershell
$env:DB_DIALECT="mysql"
$env:DB_HOST="127.0.0.1"
$env:DB_PORT="3306"
$env:DB_USER="root"
$env:DB_PASSWORD="123456"
$env:DB_NAME="accounting"
```

也可以直接设置完整连接串：

```powershell
$env:DATABASE_URL="mysql+pymysql://root:123456@127.0.0.1:3306/accounting?charset=utf8mb4"
```
