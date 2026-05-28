"""FastAPI 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import categories, transactions, statistics, export

app = FastAPI(title="记账系统 API", version="1.0.0")

# CORS 允许前端跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(statistics.router)
app.include_router(export.router)


@app.get("/")
def root():
    return {"message": "记账系统 API 运行中", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
