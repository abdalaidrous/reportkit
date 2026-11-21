import unittest

from reportkit.components.table import Table, TableCell, TableColumn, TableRow, TableStyle
from reportkit.components.typography import Text
from reportkit.styles.style import Style

from .helpers import export_html


class TableValidationTests(unittest.TestCase):
    """Validation lives in validators and runs on construction."""

    def test_column_rules(self):
        with self.assertRaises(ValueError):
            TableColumn(key="", title="x")
        with self.assertRaises(ValueError):
            TableColumn(key="a", title="x", align="middle")
        with self.assertRaises(ValueError):
            TableColumn(key="a", title="x", width="10px; color: red")
        with self.assertRaises(ValueError):
            TableColumn(key="a", title="x", format="money")

    def test_cell_rejects_value_and_children(self):
        with self.assertRaises(ValueError):
            TableCell(value="x", children=[Text(value="y")])

    def test_cell_rejects_non_component_children(self):
        with self.assertRaises(TypeError):
            TableCell(children=["text"])

    def test_row_rules(self):
        with self.assertRaises(ValueError):
            TableRow(kind="unknown")
        with self.assertRaises(TypeError):
            TableRow(cells=["x"])

    def test_table_rules(self):
        with self.assertRaises(ValueError):
            Table(columns=[])
        with self.assertRaises(ValueError):
            Table(columns=[TableColumn(key="a", title="A"), TableColumn(key="a", title="B")])
        with self.assertRaises(ValueError):
            Table(columns=[TableColumn(key="a", title="A")], table_style=TableStyle(layout="grid"))


class TableRenderingTests(unittest.TestCase):
    """Rendering of plain values, custom cells and lazy rows."""

    columns = [TableColumn(key="date", title="Date"), TableColumn(key="amount", title="Amount", format="number")]

    def test_custom_cell_renders_children_with_their_styles(self):
        cell = TableCell(children=[Text(value="2026-11-21"), Text(value="10:30 AM", style=Style(font_size=10, color="#777777")), Text(value="تم الدفع")])
        html = export_html(Table(columns=self.columns, rows=[TableRow(values={"date": cell, "amount": 500})]))
        self.assertIn('class="rk-table-cell__content"', html)
        self.assertIn("font-size: 10px; color: #777777", html)
        self.assertIn("تم الدفع", html)

    def test_plain_values_still_work(self):
        html = export_html(Table(columns=self.columns, rows=[TableRow(values={"date": "2026-11-21", "amount": 500})]))
        self.assertIn('<span class="rk-table-cell__value">2026-11-21</span>', html)
        self.assertIn("rk-table-cell--positive", html)
        self.assertIn("500.00", html)

    def test_values_are_escaped(self):
        html = export_html(Table(columns=self.columns, rows=[TableRow(values={"date": "<b>x</b>", "amount": None}), TableRow(values={"date": TableCell(value="<i>y</i>")})]))
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", html)
        self.assertIn("&lt;i&gt;y&lt;/i&gt;", html)
        self.assertNotIn("<b>x</b>", html)

    def test_cell_inherits_column_alignment(self):
        columns = [TableColumn(key="a", title="A", align="center")]
        html = export_html(Table(columns=columns, rows=[TableRow(values={"a": TableCell(value="x")}), TableRow(values={"a": TableCell(value="y", align="end")})]))
        self.assertIn("text-align: center", html)
        self.assertIn("text-align: end", html)

    def test_footer_uses_shared_cell_template(self):
        html = export_html(Table(columns=self.columns, rows=[], footer=TableRow(values={"date": "Total", "amount": 1}, kind="total")))
        self.assertIn('<tr class="rk-table-row rk-table-total"', html)
        self.assertIn('<span class="rk-table-cell__value">Total</span>', html)

    def test_rows_are_consumed_lazily(self):
        consumed = []

        def rows():
            for index in range(3):
                consumed.append(index)
                yield TableRow(values={"date": f"d{index}"})

        table = Table(columns=self.columns, rows=rows())
        self.assertEqual(consumed, [])
        html = export_html(table)
        self.assertEqual(consumed, [0, 1, 2])
        self.assertIn("d2", html)

    def test_invalid_lazy_row_is_rejected(self):
        with self.assertRaises(TypeError):
            export_html(Table(columns=self.columns, rows=iter(["not a row"])))

    def test_table_classes_follow_options(self):
        html = export_html(Table(columns=self.columns, table_style=TableStyle(ruled=True, layout="auto", repeat_header=False, avoid_row_break=False)))
        self.assertIn('class="rk-table rk-table--layout-auto rk-table--bordered rk-table--ruled"', html)

    def test_nowrap_column(self):
        columns = [TableColumn(key="a", title="A", nowrap=True)]
        html = export_html(Table(columns=columns, rows=[TableRow(values={"a": "x"})]))
        self.assertIn("rk-table-th--nowrap", html)
        self.assertIn('class="rk-table-cell rk-table-cell--nowrap"', html)


if __name__ == "__main__":
    unittest.main()
