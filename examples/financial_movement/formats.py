"""
Example 3 — one report, every format: TableBuilder with native values, lazily read rows, a repeated header and footer.

- TableBuilder defines the columns one by one; the columns format native values (Decimal, datetime) for display,
  while Excel keeps them as real numbers and dates.
- fetch_movements() is a generator standing in for a database cursor: rows are read one at a time, never loaded
  into a list. A generator is read once, so the report is rebuilt for each export.
- repeat=True puts the header and footer on every printed page (PDF and Word). They print inside the page
  margins, so they stay short (brand_line) and the top and bottom margins leave room for them.

Run from the project root:

    python -m examples.financial_movement.formats

Writes formats.html, formats.xlsx, formats_data.xlsx, formats.docx and, when WeasyPrint is installed, formats.pdf
to examples/financial_movement/output/.
"""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

from reportkit.builders import ReportBuilder, TableBuilder
from reportkit.components.typography import Text
from reportkit.exporters.excel import ExcelOptions
from reportkit.rendering.context import RenderingContext
from reportkit.styles.style import Style

from .blocks import brand_line, report_title
from .data import BRANDING
from .styles import MOVEMENTS_TABLE, TABLE

OUTPUT = Path(__file__).with_name('output')
CONTEXT = RenderingContext(language='ar', direction='rtl')

RECORDS = [
    ('000003', datetime(2026, 11, 14, 0, 47), 'دفعة الحجز رقم 1', 'الدفع نقدًا', Decimal('200.00')),
    ('000002', datetime(2026, 11, 13, 23, 55), 'دفعة الحجز رقم 1', 'الدفع نقدًا', Decimal('100.00')),
    ('000001', datetime(2026, 11, 13, 23, 39), 'دفعة الحجز رقم 1', 'تمارا', Decimal('100.00')),
]
TOTAL = {'voucher': 'الإجمالي', 'amount': Decimal('400.00')}  # Summed by the application, not by ReportKit.


def fetch_movements():
    """
    Yield prepared rows one at a time, as a database cursor would.
    """
    for voucher, created_at, description, method, amount in RECORDS:
        yield {'voucher': voucher, 'date': created_at, 'description': description, 'method': method, 'amount': amount}


def movements_table():
    """
    Columns defined one by one; format, date_format and currency control how values are displayed.
    """
    return (
        TableBuilder()
        .column('voucher', 'رقم السند', subtitle='Voucher No.', align='center', nowrap=True)
        .column('date', 'التاريخ والوقت', subtitle='Date & Time', format='datetime', date_format='%d/%m/%Y %I:%M %p', align='center', nowrap=True)
        .column('description', 'البيان', subtitle='Description')
        .column('method', 'طريقة الدفع', subtitle='Payment Method', align='center')
        .column('amount', 'المبلغ', subtitle='Amount', format='currency', currency='﷼', align='center', nowrap=True)
        .rows(fetch_movements())
        .totals(TOTAL)
        .style(TABLE)
        .table_style(MOVEMENTS_TABLE)
        .build()
    )


def report_builder():
    """
    The header and footer repeat on every page, inside the page margins: keep them short and the margins tall enough.
    """
    return (
        ReportBuilder('Financial Movement Report')
        .page(margin='20mm 11mm 16mm', page_number_position='bottom-right')
        .header(brand_line(BRANDING), repeat=True)
        .footer(Text(value='تقرير آلي — ReportKit', style=Style(font_size=8, color='#777777', text_align='center')), repeat=True)
        .add(report_title('Financial Movement Report', 'تقرير الحركة المالية'))
        .add(movements_table())
        .page_number('Page {page} of {pages}')
    )


def main():
    """
    Export the same report to every format; PDF is skipped when WeasyPrint is not installed.
    """
    OUTPUT.mkdir(exist_ok=True)
    exports = [
        ('html', 'formats.html', {}),
        ('xlsx', 'formats.xlsx', {}),
        ('xlsx', 'formats_data.xlsx', {'options': ExcelOptions(mode='data', streaming=True)}),
        ('docx', 'formats.docx', {}),
        ('pdf', 'formats.pdf', {}),
    ]
    written = []
    for format, name, options in exports:
        try:
            written.append(report_builder().export_to(format, OUTPUT / name, CONTEXT, **options))
        except ImportError as error:
            print(f'Skipped {name}: {error}')
    return written


if __name__ == '__main__':
    print(*main(), sep='\n')
