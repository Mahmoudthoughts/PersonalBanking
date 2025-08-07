from calendar import monthrange
from datetime import date
import io
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi_jwt_auth import AuthJWT
from jinja2 import Environment, FileSystemLoader, select_autoescape

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from ..models import Transaction


templates = Environment(
    loader=FileSystemLoader(Path(__file__).resolve().parent.parent / "templates"),
    autoescape=select_autoescape(["html"]),
)

router = APIRouter()


@router.get("/{month}", response_class=HTMLResponse)
def monthly_report(
    month: str,
    format: Optional[str] = Query(None),
    Authorize: AuthJWT = Depends(),
):
    """Return an HTML or PDF spending report for the given month."""
    Authorize.jwt_required()
    logger = logging.getLogger(__name__)
    logger.info("Generating report for %s", month)
    try:
        start = date.fromisoformat(f"{month}-01")
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid month")

    last_day = monthrange(start.year, start.month)[1]
    end = date(start.year, start.month, last_day)

    transactions = (
        Transaction.query
        .filter(Transaction.transaction_date >= start)
        .filter(Transaction.transaction_date <= end)
        .all()
    )

    total = sum(float(t.total_amount or 0) for t in transactions)
    by_cardholder = {}
    for t in transactions:
        name = t.cardholder_name or "Unknown"
        by_cardholder[name] = by_cardholder.get(name, 0) + float(t.total_amount or 0)

    html = templates.get_template("report.html").render(
        month=start.strftime("%B %Y"),
        total=total,
        by_cardholder=by_cardholder,
        transactions=transactions,
    )

    if format == "pdf":
        logger.debug("Rendering PDF report for %s", month)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(f"Spending Report - {start.strftime('%B %Y')}", styles['Title']))
        story.append(Paragraph(f"Total Spend: {total:.2f}", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph('By Cardholder', styles['Heading2']))
        for name, amount in by_cardholder.items():
            story.append(Paragraph(f"{name}: {amount:.2f}", styles['Normal']))
        story.append(Spacer(1, 12))
        data = [['Date', 'Description', 'Amount', 'Cardholder', 'Card Number']]
        for t in transactions:
            data.append([
                str(t.transaction_date),
                t.description,
                str(t.total_amount or 0),
                t.cardholder_name,
                t.card_number or ''
            ])
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)
        doc.build(story)
        buffer.seek(0)
        headers = {"Content-Disposition": f"attachment; filename=report-{month}.pdf"}
        return StreamingResponse(buffer, media_type="application/pdf", headers=headers)

    logger.debug('Returning HTML report for %s', month)
    return HTMLResponse(content=html)
