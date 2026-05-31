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

## Error Response Spec

后端统一返回以下错误结构：

```json
{
  "code": 400,
  "message": "验证码错误或已过期",
  "detail": "验证码错误或已过期"
}
```

字段说明：

- `code`: HTTP 状态码
- `message`: 面向业务的错误描述
- `detail`: 与前端兼容的错误文案字段（可直接展示）

参数校验失败（422）时，额外包含：

```json
{
  "code": 422,
  "message": "请求参数校验失败",
  "detail": "请求参数校验失败",
  "errors": [
    {
      "loc": ["body", "phone"],
      "msg": "String should match pattern '^1[3-9]\\d{9}$'",
      "type": "string_pattern_mismatch"
    }
  ]
}
```

在开发环境（`APP_ENV=dev/development/local/test`）下，500 错误会额外返回 `debug` 字段，便于排查。
