# ZZGG Backend

预留的 Python + FastAPI 后端，提供给 Vant 前端联调的占位接口。

## 安装依赖

```bash
python -m pip install -r requirements.txt
```

## 启动

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 已提供接口

- `GET /api/health`：检查后端是否可用
- `POST /api/bills/preview`：接收账单表单并返回预览数据
