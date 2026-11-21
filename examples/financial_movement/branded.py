"""
Example 2 — the complete branded report: hotel header with logo, title, filters, two tables, a footer and page numbers.

This is the design of reference_preview.html with a small data set. The blocks (hotel_identity, labeled_grid...)
are plain components from blocks.py; the builder only places them in order.

Run from the project root:

    python -m examples.financial_movement.branded          # HTML
    python -m examples.financial_movement.branded --pdf    # HTML and PDF (needs WeasyPrint, see CLAUDE.md)

Writes examples/financial_movement/output/branded.html (and branded.pdf).
"""

import sys
from pathlib import Path

from reportkit.builders import ReportBuilder
from reportkit.rendering.context import RenderingContext

from .blocks import hotel_identity, labeled_grid, report_title, section_title
from .data import BRANDING, FILTERS, METADATA, MOVEMENT_COLUMNS, MOVEMENTS, SUMMARY_COLUMNS, SUMMARY_ROWS, SUMMARY_TOTAL
from .styles import MOVEMENTS_TABLE, SUMMARY_TABLE, TABLE

OUTPUT = Path(__file__).with_name('output')
CONTEXT = RenderingContext(language='ar', direction='rtl')


def report_builder():
    """
    Lay the report out top to bottom; the builder keeps the header first and the footer and page number last.
    """
    return (
        ReportBuilder('Financial Movement Report')
        .page(size='A4', orientation='portrait', margin='10mm 11mm 12mm', page_number_position='bottom-center')
        .header(hotel_identity(BRANDING))
        .add(report_title('Financial Movement Report', 'تقرير الحركة المالية'))
        .add(labeled_grid(FILTERS))
        .table(MOVEMENT_COLUMNS, MOVEMENTS, style=TABLE, table_style=MOVEMENTS_TABLE)
        .spacer(20)
        .add(section_title('Summary by Payment Method', 'الملخص حسب طريقة الدفع'))
        .table(SUMMARY_COLUMNS, SUMMARY_ROWS, totals=SUMMARY_TOTAL, style=TABLE, table_style=SUMMARY_TABLE)
        .spacer(20)
        .footer(labeled_grid(METADATA, framed=True))
        .page_number('Page {page} of {pages}')
    )


def main(formats=('html',)):
    """
    Export the report once per requested format.
    """
    OUTPUT.mkdir(exist_ok=True)
    builder = report_builder()
    return [builder.export_to(format, OUTPUT / f'branded.{format}', CONTEXT) for format in formats]


if __name__ == '__main__':
    print(*main(('html', 'pdf') if '--pdf' in sys.argv else ('html',)), sep='\n')
