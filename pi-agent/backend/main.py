"""FastAPI 入口"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import APP_ENV
from init_db import init_database
from routers import auth, categories, transactions, statistics, export

app = FastAPI(title="ZG记账系统 API", version="1.0.0")


def _detail_to_message(detail) -> str:
    if isinstance(detail, str) and detail.strip():
        return detail
    return "请求失败"


@app.on_event("startup")
def startup_init_database():
    init_database()


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    message = _detail_to_message(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": message,
            "detail": message,
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_request: Request, exc: RequestValidationError):
    message = "请求参数校验失败"
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": message,
            "detail": message,
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    message = "服务器内部错误"
    response = {
        "code": 500,
        "message": message,
        "detail": message,
    }
    if APP_ENV.lower() in {"dev", "development", "local", "test"}:
        response["debug"] = str(exc)
    return JSONResponse(status_code=500, content=response)

# CORS 允许前端跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(statistics.router)
app.include_router(export.router)


@app.get("/")
def root():
    return {"message": "ZG记账系统 API 运行中", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
