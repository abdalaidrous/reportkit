import io
import unittest

from examples.financial_movement.blocks import hotel_identity, labeled_grid, report_title, section_title
from examples.financial_movement.branded import report_builder
from examples.financial_movement.data import BRANDING, FILTERS, METADATA, MOVEMENT_COLUMNS, MOVEMENTS, SUMMARY_COLUMNS, SUMMARY_ROWS, SUMMARY_TOTAL
from examples.financial_movement.styles import MOVEMENTS_TABLE, SUMMARY_TABLE, TABLE
from reportkit.builders import ReportBuilder, TableBuilder
from reportkit.builders.report import expand_margin
from reportkit.components.document import Footer, Header, Page, Report
from reportkit.components.layout import Spacer
from reportkit.components.pagination import PageNumber
from reportkit.components.table import Table, TableColumn, TableRow, TableStyle
from reportkit.components.typography import Text
from reportkit.exporters.html.exporter import HtmlExporter
from reportkit.rendering.context import RenderingContext


CONTEXT = RenderingContext(language="ar", direction="rtl")
COLUMNS = [TableColumn(key="name", title="Name"), TableColumn(key="amount", title="Amount")]


def html(report):
    """
    Export a report to HTML text.
    """
    return HtmlExporter().export(report, CONTEXT).decode("utf-8")


def direct_report():
    """
    Build the branded example tree directly from components, without the builder.
    """
    return Report(title="Financial Movement Report", children=[Page(
        size="A4", orientation="portrait", margin_top="10mm", margin_right="11mm", margin_bottom="12mm", margin_left="11mm",
        page_number_position="bottom-center",
        children=[
            Header(children=[hotel_identity(BRANDING)]),
            report_title("Financial Movement Report", "تقرير الحركة المالية"),
            labeled_grid(FILTERS),
            Table(columns=MOVEMENT_COLUMNS, rows=[TableRow(values=row) for row in MOVEMENTS], style=TABLE, table_style=MOVEMENTS_TABLE),
            Spacer(height=20),
            section_title("Summary by Payment Method", "الملخص حسب طريقة الدفع"),
            Table(columns=SUMMARY_COLUMNS, rows=[TableRow(values=row) for row in SUMMARY_ROWS], footer=TableRow(values=SUMMARY_TOTAL, kind="total"), style=TABLE, table_style=SUMMARY_TABLE),
            Spacer(height=20),
            Footer(children=[labeled_grid(METADATA, framed=True)]),
            PageNumber(format="Page {page} of {pages}"),
        ],
    )])


class ReportBuilderTests(unittest.TestCase):
    """
    ReportBuilder produces the same tree as direct construction and keeps it in a valid order.
    """

    def test_matches_direct_construction(self):
        self.assertEqual(html(report_builder().build()), html(direct_report()))

    def test_repeated_footer_precedes_content(self):
        content = Text(value="body")
        page = ReportBuilder().add(content).footer(Text(value="f"), repeat=True).header(Text(value="h")).page_number().build().children[0]
        self.assertEqual([type(child) for child in page.children], [Header, Footer, Text, PageNumber])

    def test_margin_shorthand(self):
        self.assertEqual(expand_margin("1mm"), dict.fromkeys(["margin_top", "margin_right", "margin_bottom", "margin_left"], "1mm"))
        self.assertEqual(expand_margin("1mm 2mm 3mm"), {"margin_top": "1mm", "margin_right": "2mm", "margin_bottom": "3mm", "margin_left": "2mm"})
        with self.assertRaises(ValueError):
            expand_margin("1 2 3 4 5")

    def test_explicit_margin_overrides_shorthand(self):
        page = ReportBuilder().page(margin="5mm", margin_left="9mm").build().children[0]
        self.assertEqual((page.margin_top, page.margin_left), ("5mm", "9mm"))

    def test_export_by_format(self):
        builder = ReportBuilder("Export").table(COLUMNS, [{"name": "a", "amount": 1}])
        self.assertTrue(builder.export("html", CONTEXT).startswith(b"<!DOCTYPE html>"))
        stream = io.BytesIO()
        builder.export_to("html", stream, CONTEXT)
        self.assertIn("rk-table", stream.getvalue().decode("utf-8"))

    def test_unknown_format(self):
        with self.assertRaises(ValueError):
            ReportBuilder().export("odt")


class TableBuilderTests(unittest.TestCase):
    """
    TableBuilder wraps prepared rows lazily and never calculates.
    """

    def test_rows_stay_lazy_and_reiterable(self):
        reads = []

        def source():
            for index in range(3):
                reads.append(index)
                yield {"name": str(index), "amount": index}

        table = TableBuilder().columns(*COLUMNS).rows(source()).build()
        self.assertEqual(reads, [])
        self.assertEqual([row.values["name"] for row in table.rows], ["0", "1", "2"])

        listed = TableBuilder().columns(*COLUMNS).rows([{"name": "a", "amount": 1}]).build()
        self.assertEqual(list(listed.rows), list(listed.rows))

    def test_totals_become_total_row(self):
        table = TableBuilder().column("name", "Name").totals({"name": "Total"}).build()
        self.assertEqual(table.footer, TableRow(values={"name": "Total"}, kind="total"))

    def test_ready_rows_are_kept(self):
        row = TableRow(values={"name": "a"}, kind="subtotal")
        table = TableBuilder().column("name", "Name").rows([row]).build()
        self.assertIs(next(iter(table.rows)), row)

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            list(TableBuilder().column("name", "Name").rows([["a"]]).build().rows)
        with self.assertRaises(TypeError):
            TableBuilder().table_style(TableStyle(), striped=True)
        with self.assertRaises(ValueError):
            TableBuilder().build()


if __name__ == "__main__":
    unittest.main()
