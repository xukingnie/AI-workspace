"""导出路由：Excel / PDF"""
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from services.export_excel import export_excel
from services.export_pdf import export_pdf

router = APIRouter(prefix="/api/export", tags=["导出"])


@router.get("/excel")
def download_excel(
    start_date: date | None = Query(None, description="开始日期"),
    end_date: date | None = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
):
    """导出账单为 Excel 文件"""
    output = export_excel(db, start_date, end_date)
    filename = "账单明细.xlsx"
    if start_date and end_date:
        filename = f"账单明细_{start_date}_{end_date}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/pdf")
def download_pdf(
    start_date: date | None = Query(None, description="开始日期"),
    end_date: date | None = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
):
    """导出账单为 PDF 文件"""
    output = export_pdf(db, start_date, end_date)
    filename = "账单明细.pdf"
    if start_date and end_date:
        filename = f"账单明细_{start_date}_{end_date}.pdf"

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
