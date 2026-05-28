"""PDF 导出服务"""
import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from sqlalchemy.orm import Session, joinedload

from models import Transaction

# 尝试注册中文字体（需要系统有中文字体）
try:
    pdfmetrics.registerFont(TTFont("SimSun", "C:/Windows/Fonts/simsun.ttc"))
    CN_FONT = "SimSun"
except Exception:
    # 回退到默认字体（不支持中文）
    CN_FONT = "Helvetica"


def export_pdf(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
) -> io.BytesIO:
    """导出账单数据为 PDF 文件，返回 BytesIO"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CNTitle",
        parent=styles["Title"],
        fontName=CN_FONT,
        fontSize=18,
        spaceAfter=10 * mm,
        alignment=1,  # 居中
    )
    normal_style = ParagraphStyle(
        "CNNormal",
        parent=styles["Normal"],
        fontName=CN_FONT,
        fontSize=10,
        leading=14,
    )

    elements = []

    # 标题
    title_text = "记账系统 - 账单明细"
    if start_date and end_date:
        title_text += f"（{start_date} ~ {end_date}）"
    elif start_date:
        title_text += f"（{start_date} 起）"
    elif end_date:
        title_text += f"（截至 {end_date}）"
    elements.append(Paragraph(title_text, title_style))
    elements.append(Spacer(1, 5 * mm))

    # 查询数据
    q = db.query(Transaction).options(joinedload(Transaction.category))
    if start_date:
        q = q.filter(Transaction.transaction_date >= start_date)
    if end_date:
        q = q.filter(Transaction.transaction_date <= end_date)
    transactions = q.order_by(
        Transaction.transaction_date.desc(), Transaction.created_at.desc()
    ).all()

    # 表格
    table_data = [["日期", "类型", "分类", "金额", "备注"]]
    income_total = 0.0
    expense_total = 0.0

    for txn in transactions:
        type_text = "收入" if txn.type == "income" else "支出"
        amount = float(txn.amount)
        table_data.append([
            str(txn.transaction_date),
            type_text,
            txn.category.name if txn.category else "",
            f"{amount:.2f}",
            txn.note or "",
        ])
        if txn.type == "income":
            income_total += amount
        else:
            expense_total += amount

    # 汇总行
    table_data.append(["", "", "收入合计", f"{income_total:.2f}", ""])
    table_data.append(["", "", "支出合计", f"{expense_total:.2f}", ""])
    table_data.append(["", "", "结余", f"{income_total - expense_total:.2f}", ""])

    col_widths = [80, 40, 70, 65, 200]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    table.setStyle(
        TableStyle([
            # 表头
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), CN_FONT),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            # 边框
            ("GRID", (0, 0), (-1, -4), 0.5, colors.grey),
            ("GRID", (0, -3), (-1, -1), 0.5, colors.grey),
            ("LINEBELOW", (0, 0), (-1, 0), 1, colors.grey),
            # 汇总行样式
            ("BACKGROUND", (0, -3), (-1, -3), colors.HexColor("#E2EFDA")),
            ("BACKGROUND", (0, -2), (-1, -2), colors.HexColor("#FCE4D6")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#D9E2F3")),
            ("FONTNAME", (0, -1), (-1, -1), CN_FONT),
        ])
    )

    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
