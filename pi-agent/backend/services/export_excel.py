"""Excel 导出服务"""
import io
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from sqlalchemy.orm import Session, joinedload

from models import Transaction


def export_excel(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
) -> io.BytesIO:
    """导出账单数据为 Excel 文件，返回 BytesIO"""
    wb = Workbook()
    ws = wb.active
    ws.title = "账单记录"

    # 样式定义
    header_font = Font(name="微软雅黑", bold=True, size=12, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    cell_alignment = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    # 标题行
    ws.merge_cells("A1:F1")
    title = "记账系统 - 账单明细"
    if start_date and end_date:
        title += f"（{start_date} ~ {end_date}）"
    elif start_date:
        title += f"（{start_date} 起）"
    elif end_date:
        title += f"（截至 {end_date}）"
    ws["A1"] = title
    ws["A1"].font = Font(name="微软雅黑", bold=True, size=16)
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

    # 表头
    headers = ["日期", "类型", "分类", "金额", "备注", "记录时间"]
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    # 查询数据
    q = db.query(Transaction).options(joinedload(Transaction.category))
    if start_date:
        q = q.filter(Transaction.transaction_date >= start_date)
    if end_date:
        q = q.filter(Transaction.transaction_date <= end_date)
    transactions = q.order_by(
        Transaction.transaction_date.desc(), Transaction.created_at.desc()
    ).all()

    # 数据行
    income_total = 0.0
    expense_total = 0.0
    for row_idx, txn in enumerate(transactions, 4):
        type_text = "收入" if txn.type == "income" else "支出"
        amount = float(txn.amount)

        ws.cell(row=row_idx, column=1, value=str(txn.transaction_date))
        ws.cell(row=row_idx, column=2, value=type_text)
        ws.cell(
            row=row_idx,
            column=3,
            value=txn.category.name if txn.category else "",
        )
        ws.cell(row=row_idx, column=4, value=amount)
        ws.cell(row=row_idx, column=5, value=txn.note or "")
        ws.cell(row=row_idx, column=6, value=txn.created_at.strftime("%Y-%m-%d %H:%M"))

        for col in range(1, 7):
            ws.cell(row=row_idx, column=col).alignment = cell_alignment
            ws.cell(row=row_idx, column=col).border = thin_border

        if txn.type == "income":
            income_total += amount
        else:
            expense_total += amount

    # 汇总行
    summary_row = len(transactions) + 4
    ws.merge_cells(start_row=summary_row, start_column=1, end_row=summary_row, end_column=3)
    ws.cell(row=summary_row, column=1, value="合计")
    ws.cell(row=summary_row, column=1).font = Font(name="微软雅黑", bold=True)
    ws.cell(row=summary_row, column=1).alignment = cell_alignment

    ws.cell(row=summary_row, column=4, value=round(income_total, 2))
    ws.cell(row=summary_row, column=4).font = Font(name="微软雅黑", color="008000", bold=True)

    summary_row2 = summary_row + 1
    ws.merge_cells(start_row=summary_row2, start_column=1, end_row=summary_row2, end_column=3)
    ws.cell(row=summary_row2, column=1, value="收入合计")
    ws.cell(row=summary_row2, column=4, value=round(income_total, 2))
    ws.cell(row=summary_row2, column=4).font = Font(name="微软雅黑", color="008000")

    summary_row3 = summary_row + 2
    ws.merge_cells(start_row=summary_row3, start_column=1, end_row=summary_row3, end_column=3)
    ws.cell(row=summary_row3, column=1, value="支出合计")
    ws.cell(row=summary_row3, column=4, value=round(expense_total, 2))
    ws.cell(row=summary_row3, column=4).font = Font(name="微软雅黑", color="FF0000")

    summary_row4 = summary_row + 3
    ws.merge_cells(start_row=summary_row4, start_column=1, end_row=summary_row4, end_column=3)
    ws.cell(row=summary_row4, column=1, value="结余")
    ws.cell(row=summary_row4, column=4, value=round(income_total - expense_total, 2))

    for r in range(summary_row, summary_row4 + 1):
        for c in range(1, 7):
            ws.cell(row=r, column=c).border = thin_border
            ws.cell(row=r, column=c).alignment = cell_alignment

    # 列宽
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 8
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 24
    ws.column_dimensions["F"].width = 18

    # 冻结首行
    ws.freeze_panes = "A4"

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
