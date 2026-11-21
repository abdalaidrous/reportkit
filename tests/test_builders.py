import io
import unittest

from examples.financial_movement.data import FILTERS, METADATA, MOVEMENT_COLUMNS, MOVEMENTS, SUMMARY_COLUMNS, SUMMARY_ROWS, SUMMARY_TOTAL
from examples.financial_movement.report import build_header, build_report, build_table, filters_grid, report_title, section_title
from examples.financial_movement.styles import TABLE
from reportkit.builders import ReportBuilder, TableBuilder
from reportkit.builders.report import expand_margin
from reportkit.components.document import Footer, Header
from reportkit.components.pagination import PageNumber
from reportkit.components.table import TableColumn, TableRow, TableStyle
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


def financial_movement_report():
    """
    Rebuild the financial movement example through ReportBuilder, calling the footer early on purpose.
    """
    movements = build_table(MOVEMENT_COLUMNS, MOVEMENTS)
    summary = build_table(SUMMARY_COLUMNS, SUMMARY_ROWS, SUMMARY_TOTAL, first_align="right", ruled=True)
    return (
        ReportBuilder("Financial Movement Report")
        .page(size="A4", orientation="portrait", margin="10mm 11mm 12mm", page_number_position="bottom-center")
        .footer(filters_grid(METADATA, framed=True))
        .header(*build_header().children)
        .add(report_title("Financial Movement Report", "تقرير الحركة المالية"), filters_grid(FILTERS))
        .table(movements.columns, MOVEMENTS, style=TABLE, table_style=movements.table_style)
        .spacer(20)
        .add(section_title("Summary by Payment Method", "الملخص حسب طريقة الدفع"))
        .table(summary.columns, SUMMARY_ROWS, totals=SUMMARY_TOTAL, style=TABLE, table_style=summary.table_style)
        .spacer(20)
        .page_number("Page {page} of {pages}")
        .build()
    )


class ReportBuilderTests(unittest.TestCase):
    """
    ReportBuilder produces the same tree as direct construction and keeps it in a valid order.
    """

    def test_matches_direct_construction(self):
        self.assertEqual(html(financial_movement_report()), html(build_report()))

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
