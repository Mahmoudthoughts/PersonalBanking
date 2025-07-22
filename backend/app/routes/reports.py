from calendar import monthrange
from datetime import date
import io

from flask import Blueprint, render_template, request, send_file, current_app
from flask_jwt_extended import jwt_required

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from ..models import Transaction

bp = Blueprint('reports', __name__, url_prefix='/reports')


@bp.route('/<month>', methods=['GET'])
@jwt_required()
def monthly_report(month: str):
    """Return an HTML or PDF spending report for the given month.

    ``month`` is expected in ``YYYY-MM`` format.
    """
    current_app.logger.info('Generating report for %s', month)
    try:
        start = date.fromisoformat(f"{month}-01")
    except ValueError:
        return {"error": "invalid month"}, 400

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

    html = render_template(
        'report.html',
        month=start.strftime('%B %Y'),
        total=total,
        by_cardholder=by_cardholder,
        transactions=transactions,
    )

    if request.args.get('format') == 'pdf':
        current_app.logger.debug('Rendering PDF report for %s', month)
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
        data = [['Date', 'Description', 'Amount', 'Cardholder']]
        for t in transactions:
            data.append([
                str(t.transaction_date),
                t.description,
                str(t.total_amount or 0),
                t.cardholder_name
            ])
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)
        doc.build(story)
        buffer.seek(0)
        response = send_file(
            buffer,
            mimetype='application/pdf',
            download_name=f'report-{month}.pdf'
        )
        return response

    current_app.logger.debug('Returning HTML report for %s', month)
    return html
