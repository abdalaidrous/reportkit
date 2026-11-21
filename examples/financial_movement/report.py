"""Build the supplied financial movement report with ReportKit components."""

from pathlib import Path

from reportkit.components.document import Report, Page, Header, Footer
from reportkit.components.layout import Box, Grid, Row, Column, Section, Spacer
from reportkit.components.typography import Text, Heading
from reportkit.components.table import Table, TableColumn, TableRow, TableStyle
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
    return Grid(style=Style(direction='ltr'), columns=2, children=[
        KeyValue(label=en, secondary_label=ar, value=value, style=Style(direction='ltr', text_align='left'))
        for en, value, ar in items
    ])


def title_row(english, arabic):
    """Build the bilingual section heading."""
    return Grid(style=Style(direction='ltr'), columns='1fr 1fr', children=[
        Text(value=english, style=SECONDARY.merge(Style(text_align='left'))),
        Heading(value=arabic, level=3, style=TITLE.merge(Style(text_align='right'))),
    ])


HEADER_BORDER = '1px solid #dedede'
ID_LABEL = Style(font_size=9, color='#777777', margin=0)
ID_VALUE = Style(font_size=11, font_weight=700, margin=0, direction='ltr')
LEFT = Style(text_align='left', margin=0)
RIGHT = Style(text_align='right', margin=0)


def id_cell(ar_label, value, en_label, divider=False, style=None):
    """One bilingual cell laid out as: Arabic label | value | English label.

    ``divider`` draws the separator on the cell's left edge, so set it on the
    right-hand (first) cell of an RTL grid.
    """
    cell_style = Style(direction='rtl', padding='8px 12px', border_left=HEADER_BORDER if divider else None)
    return Row(justify='space-between', align='center', gap='8px',
        style=cell_style.merge(style) if style else cell_style,
        children=[Text(value=ar_label, style=ID_LABEL), Text(value=value, style=ID_VALUE), Text(value=en_label, style=ID_LABEL)])


FILTER_BORDER = '1px solid #e5e5e5'


def report_title(english, arabic):
    """Arabic title on the right, English subtitle on the left, heavy rule underneath."""
    return Grid(columns='1fr 1fr', style=Style(direction='rtl', gap=16, align_items='center', padding='4px 0 10px', border_bottom='2px solid #222222'), children=[
        Heading(value=arabic, level=2, style=Style(font_size=20, font_weight=700, text_align='right', margin=0)),
        Text(value=english, style=Style(font_size=11, color='#555555', letter_spacing=0.5, text_align='left', margin=0)),
    ])


def section_title(english, arabic):
    """Bold Arabic section title on the right, small English title on the left."""
    return Grid(columns='1fr 1fr', style=Style(direction='rtl', gap=16, align_items='end', margin_bottom=6), children=[
        Heading(value=arabic, level=3, style=Style(font_size=14, font_weight=700, text_align='right', margin=0)),
        Text(value=english, style=Style(font_size=10, color='#555555', text_align='left', margin=0)),
    ])


def filters_grid(items, framed=False):
    """Two-column RTL grid of bilingual cells; items are (english, value, arabic)."""
    cells = list(items) + ([None] if len(items) % 2 else [])
    last_row = (len(cells) - 1) // 2
    children = []
    for index, item in enumerate(cells):
        cell_style = Style(border_bottom=FILTER_BORDER if index // 2 < last_row else None)
        divider = index % 2 == 0
        if item is None:
            children.append(Box(style=cell_style.merge(Style(border_left=HEADER_BORDER if divider else None))))
        else:
            english, value, arabic = item
            children.append(id_cell(arabic, value, english, divider=divider, style=cell_style.merge(Style(padding='10px 14px'))))
    frame = Style(border_width=1, border_style='solid', border_color='#dedede', border_radius=6, overflow='hidden') if framed else Style()
    return Grid(columns='1fr 1fr', style=frame.merge(Style(direction='rtl', gap=0, margin_bottom=14)), children=children)


def build_header():
    """Build the bordered bilingual hotel identity box with its identifier strip."""
    return Header(children=[Box(
        style=Style(border_width=1, border_style='solid', border_color='#dedede', border_radius=6, overflow='hidden', margin_bottom=14),
        children=[
            Grid(columns='1fr auto 1fr', style=Style(direction='rtl', gap=16, padding='14px 16px', align_items='center'), children=[
                Column(direction='rtl', align='start', gap='2px', children=[Heading(value=BRANDING['name_ar'], level=2, style=BRAND_NAME.merge(RIGHT)), Text(value=BRANDING['location_ar'], style=SECONDARY.merge(RIGHT)), Text(value=BRANDING['address_ar'], style=SECONDARY.merge(RIGHT))]),
                Image(src=LOGO.as_uri(), alt='Hotel logo', width='76', height='76'),
                Column(direction='ltr', align='start', gap='2px', children=[Heading(value=BRANDING['name_en'], level=2, style=BRAND_NAME.merge(LEFT)), Text(value=BRANDING['location_en'], style=SECONDARY.merge(LEFT)), Text(value=BRANDING['address_en'], style=SECONDARY.merge(LEFT))]),
            ]),
            Grid(columns='1fr 1fr', style=Style(direction='rtl', gap=0, background_color='#f5f5f5', border_top=HEADER_BORDER), children=[
                id_cell('الرقم الضريبي', BRANDING['vat'], 'VAT No', divider=True),
                id_cell('السجل التجاري', BRANDING['cr'], 'C.R'),
            ]),
        ])])


def build_table(columns, rows, footer=None, first_align='center', ruled=False):
    """Display prepared rows and optional prepared footer; columns are (key, ar, en, width, nowrap)."""
    table_columns = [
        TableColumn(key=key, title=title, subtitle=subtitle, width=width, nowrap=nowrap,
                    align=first_align if index == 0 else 'center', header_align=first_align if index == 0 else 'center')
        for index, (key, title, subtitle, width, nowrap) in enumerate(columns)
    ]
    table_rows = [TableRow(values=row) for row in rows]
    total_row = TableRow(values=footer, kind='total') if footer is not None else None
    return Table(columns=table_columns, rows=table_rows, footer=total_row, style=TABLE,
                 table_style=TableStyle(bordered=False, ruled=ruled, layout='auto'))


def build_report():
    """Assemble the report without calculating or grouping values."""
    return Report(title='Financial Movement Report', children=[Page(size='A4', orientation='portrait', margin_top='10mm', margin_right='11mm', margin_bottom='12mm', margin_left='11mm', page_number_position='bottom-center', children=[
        build_header(),
        report_title('Financial Movement Report', 'تقرير الحركة المالية'),
        filters_grid(FILTERS),
        build_table(MOVEMENT_COLUMNS, MOVEMENTS),
        Spacer(height=20),
        section_title('Summary by Payment Method', 'الملخص حسب طريقة الدفع'),
        build_table(SUMMARY_COLUMNS, SUMMARY_ROWS, SUMMARY_TOTAL, first_align='right', ruled=True),
        Spacer(height=20),
        Footer(children=[filters_grid(METADATA, framed=True)]),
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
