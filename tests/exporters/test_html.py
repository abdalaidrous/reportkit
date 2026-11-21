import unittest

import reportkit.exporters.html  # noqa: F401  (registers the HTML renderers)
from reportkit.components.document import Page, Report
from reportkit.components.information import InfoGrid, KeyValue
from reportkit.components.layout import Grid
from reportkit.components.table import Table, TableCell, TableColumn, TableRow
from reportkit.components.typography import Heading, Text
from reportkit.exporters.html.direction import text_direction
from reportkit.exporters.html.exporter import HtmlExporter
from reportkit.rendering.context import RenderingContext
from reportkit.styles.style import Style


def export(*children, direction="rtl"):
    """
    Export a one-page report to HTML text.
    """
    report = Report(title="HTML test", children=[Page(children=list(children))])
    return HtmlExporter().export(report, RenderingContext(language="ar", direction=direction)).decode("utf-8")


class HtmlOutputTests(unittest.TestCase):
    """
    HTML details that keep the browser and WeasyPrint output aligned.
    """

    def test_text_has_no_padding_whitespace(self):
        html = export(Text(value="الرقم الضريبي"), Heading(value="Title", level=2))
        self.assertIn('<p class="rk-text">الرقم الضريبي</p>', html)
        self.assertIn('<h2 class="rk-heading rk-heading--2">Title</h2>', html)

    def test_grid_names_direction_and_column_count(self):
        html = export(Grid(columns="1fr auto 1fr", children=[Text(value="a")]), Grid(columns=2, style=Style(direction="ltr"), children=[Text(value="b")]))
        self.assertIn('class="rk-grid rk-grid--rtl rk-grid--cols-3"', html)
        self.assertIn('class="rk-grid rk-grid--ltr rk-grid--cols-2"', html)

    def test_info_grid_names_direction_and_column_count(self):
        html = export(InfoGrid(columns=3, children=[KeyValue(label="a", value="1")]), direction="ltr")
        self.assertIn('class="rk-info-grid rk-grid--ltr rk-grid--cols-3"', html)

    def test_cell_lines_get_their_own_direction(self):
        columns = [TableColumn(key="a", title="البيان", subtitle="Description")]
        html = export(Table(columns=columns, rows=[TableRow(values={"a": "دفعة للحجز رقم\n(RES-A-000001)"}), TableRow(values={"a": "12:47"})]))
        self.assertIn('<span class="rk-table-cell__line" dir="rtl">دفعة للحجز رقم</span><span class="rk-table-cell__line" dir="ltr">(RES-A-000001)</span>', html)
        self.assertIn('<span class="rk-table-cell__line">12:47</span>', html)
        self.assertIn('<span class="rk-table-th__subtitle" dir="ltr">Description</span>', html)

    def test_cell_lines_are_escaped(self):
        html = export(Table(columns=[TableColumn(key="a", title="A")], rows=[TableRow(values={"a": "<b>x</b>"}), TableRow(values={"a": TableCell(value="<i>y</i>")})]))
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", html)
        self.assertIn("&lt;i&gt;y&lt;/i&gt;", html)

    def test_text_direction(self):
        self.assertEqual(text_direction("(RES-A-000001)"), "ltr")
        self.assertEqual(text_direction("12:47 AM"), "ltr")
        self.assertEqual(text_direction("دفعة 12"), "rtl")
        self.assertIsNone(text_direction("2026-11-21"))


if __name__ == "__main__":
    unittest.main()
