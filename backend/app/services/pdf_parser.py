"""Utilities for parsing uploaded PDF statements."""

from datetime import date


def parse_pdf(file_path):
    """Parse transactions from a PDF statement.

    This is a placeholder implementation that simply returns a single
    transaction. Real logic would use a library such as ``pdfminer.six`` to
    extract data from the PDF file.
    """

    return [
        {
            "date": date.today(),
            "description": "Placeholder transaction",
            "amount": 0.0,
        }
    ]
