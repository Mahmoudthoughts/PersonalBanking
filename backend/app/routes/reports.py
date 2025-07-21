from calendar import monthrange
from datetime import date
import io

from flask import Blueprint, render_template, request, send_file
from weasyprint import HTML

from ..models import Transaction

bp = Blueprint('reports', __name__, url_prefix='/reports')


@bp.route('/<month>', methods=['GET'])
def monthly_report(month: str):
    """Return an HTML or PDF spending report for the given month.

    ``month`` is expected in ``YYYY-MM`` format.
    """
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
        pdf_bytes = HTML(string=html).write_pdf()
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            download_name=f'report-{month}.pdf'
        )

    return html
