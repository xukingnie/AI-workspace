from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='ZZGG FastAPI Backend', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class BillPreviewRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    amount: float = Field(gt=0)
    note: str = Field(default='', max_length=200)
    billing_date: str = Field(min_length=10, max_length=10)


class BillPreviewResponse(BaseModel):
    message: str
    received_at: str
    next_deadline: str
    bill: BillPreviewRequest


@app.get('/api/health')
def health_check() -> dict[str, str]:
    return {
        'status': 'ok',
        'message': 'FastAPI 预留接口已就绪，可供 Vant 前端联调。',
    }


@app.post('/api/bills/preview', response_model=BillPreviewResponse)
def preview_bill(payload: BillPreviewRequest) -> BillPreviewResponse:
    now = datetime.now(timezone.utc).astimezone()
    next_deadline = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return BillPreviewResponse(
        message='账单已由 FastAPI 预留接口接收。',
        received_at=now.strftime('%Y-%m-%d %H:%M:%S'),
        next_deadline=next_deadline.strftime('%Y-%m-%d %H:%M:%S'),
        bill=payload,
    )
