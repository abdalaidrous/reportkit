"""Build the supplied financial movement report with ReportKit components."""

from pathlib import Path

from reportkit.components.document import Report, Page, Header, Footer
from reportkit.components.layout import Row, Column, Section, Spacer
from reportkit.components.typography import Text, Heading
from reportkit.components.table import Table, TableColumn, TableRow
from reportkit.components.media import Image
from reportkit.components.information import KeyValue, InfoGrid
from reportkit.components.pagination import PageNumber
from reportkit.styles.style import Style

try:
    from .data import BRANDING, FILTERS, MOVEMENT_COLUMNS, MOVEMENTS, SUMMARY_COLUMNS, SUMMARY_ROWS, SUMMARY_TOTAL, METADATA
    from .styles import TITLE, SECONDARY, BRAND_NAME, SECTION_TITLE, TABLE, META
except ImportError:
    from data import BRANDING, FILTERS, MOVEMENT_COLUMNS, MOVEMENTS, SUMMARY_COLUMNS, SUMMARY_ROWS, SUMMARY_TOTAL, METADATA
    from styles import TITLE, SECONDARY, BRAND_NAME, SECTION_TITLE, TABLE, META

LOGO = Path(__file__).with_name('logo.png')


def info_row(items):
    """Display bilingual values without deriving any report data."""
    return Row(children=[KeyValue(label=f'{en} / {ar}', value=value) for en, value, ar in items])


def title_row(english, arabic):
    """Build the bilingual section heading."""
    return Row(style=SECTION_TITLE, children=[Text(value=english, style=SECONDARY), Heading(value=arabic, level=3, style=TITLE)])


def build_header():
    """Build the three-column bilingual hotel identity."""
    return Header(children=[
        Row(children=[
            Column(children=[Heading(value=BRANDING['name_en'], level=2, style=BRAND_NAME), Text(value=BRANDING['location_en'], style=SECONDARY), Text(value=BRANDING['address_en'], style=SECONDARY)]),
            Image(src=LOGO.as_uri(), alt='Hotel logo', width='76', height='76'),
            Column(children=[Heading(value=BRANDING['name_ar'], level=2, style=BRAND_NAME), Text(value=BRANDING['location_ar'], style=SECONDARY), Text(value=BRANDING['address_ar'], style=SECONDARY)]),
        ]),
        info_row([('C.R', BRANDING['cr'], 'السجل التجاري'), ('VAT No', BRANDING['vat'], 'الرقم الضريبي')]),
    ])


def build_table(columns, rows, footer=None):
    """Display prepared rows and optional prepared footer."""
    table_columns = [TableColumn(key=key, title=title, width=width, align='center') for key, title, width in columns]
    table_rows = [TableRow(values=row) for row in rows]
    total_row = TableRow(values=footer, kind='subtotal') if footer is not None else None
    return Table(columns=table_columns, rows=table_rows, footer=total_row, style=TABLE)


def build_report():
    """Assemble the report without calculating or grouping values."""
    return Report(title='Financial Movement Report', children=[Page(size='A4', orientation='portrait', margin_top='10mm', margin_right='11mm', margin_bottom='12mm', margin_left='11mm', children=[
        build_header(),
        title_row('Financial Movement Report', 'تقرير الحركة المالية'),
        info_row(FILTERS[:2]),
        info_row(FILTERS[2:]),
        Spacer(height=12),
        build_table(MOVEMENT_COLUMNS, MOVEMENTS),
        title_row('Summary by Payment Method', 'الملخص حسب طريقة الدفع'),
        build_table(SUMMARY_COLUMNS, SUMMARY_ROWS, SUMMARY_TOTAL),
        Footer(children=[info_row(METADATA[:2]), info_row(METADATA[2:])]),
        PageNumber(format='Page {page} of {pages}'),
    ])])


def export_html(destination):
    """Export through the installed ReportKit HTML exporter."""
    from reportkit.exporters.html.exporter import HtmlExporter
    from reportkit.rendering.context import RenderingContext

    exporter = HtmlExporter()
    result = exporter.export(build_report(), RenderingContext(language='ar', direction='rtl'))
    Path(destination).write_bytes(result)
    return destination


if __name__ == '__main__':
    export_html(Path(__file__).with_name('reportkit_output.html'))
