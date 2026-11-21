import sys
from datetime import date, datetime, timezone
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from unittest import mock

import pytest

openpyxl = pytest.importorskip("openpyxl")

import reportkit.exporters.excel  # noqa: E402,F401  (registers the Excel exporter)
import reportkit.exporters.html  # noqa: E402,F401
from reportkit.components.document import Header, Page, Report  # noqa: E402
from reportkit.components.information import KeyValue  # noqa: E402
from reportkit.components.layout import Grid, Row  # noqa: E402
from reportkit.components.media import Chart, Image  # noqa: E402
from reportkit.components.pagination import PageCount, PageNumber  # noqa: E402
from reportkit.components.table import Table, TableCell, TableColumn, TableRow, TableStyle  # noqa: E402
from reportkit.components.typography import Heading, Text  # noqa: E402
from reportkit.exporters.excel import ExcelExporter, ExcelExportError, ExcelOptions  # noqa: E402
from reportkit.exporters.excel.worksheet import constants as excel_constants  # noqa: E402
from reportkit.exporters.html.exporter import HtmlExporter  # noqa: E402
from reportkit.exporters.registry import ExporterRegistry  # noqa: E402
from reportkit.rendering.context import RenderingContext  # noqa: E402

LOGO = Path(__file__).resolve().parents[2] / "examples" / "financial_movement" / "logo.png"
COLUMNS = [
    TableColumn(key="name", title="البيان", subtitle="Description"),
    TableColumn(key="amount", title="المبلغ", subtitle="Amount", format="number", decimals=2),
    TableColumn(key="day", title="التاريخ", subtitle="Date", format="date", date_format="%d/%m/%Y"),
]


def report(*children, **page):
    """
    Build a one-page report.
    """
    return Report(title="Excel test", children=[Page(children=list(children), **page)])


def export(document, direction="rtl", **options):
    """
    Export to XLSX and open the result with openpyxl.
    """
    data = ExcelExporter().export(document, RenderingContext(language="ar", direction=direction), ExcelOptions(**options))
    assert data.startswith(b"PK")
    return openpyxl.load_workbook(BytesIO(data))


def cells(sheet):
    """
    Return every non-empty cell.
    """
    return [cell for row in sheet.iter_rows() for cell in row if cell.value is not None]


def find(sheet, value):
    """
    Return the first cell holding a value.
    """
    return next(cell for cell in cells(sheet) if cell.value == value)


def merged_range(sheet, value):
    """
    Return the merged range that starts at the cell holding a value.
    """
    cell = find(sheet, value)
    return next(merged for merged in sheet.merged_cells.ranges if merged.min_row == cell.row and merged.min_col == cell.column)


def movements():
    """
    Return a prepared table with a prepared footer.
    """
    rows = [TableRow(values={"name": "دفعة نقدية", "amount": Decimal("150.25"), "day": date(2026, 11, 14)}), TableRow(values={"name": "Bank transfer", "amount": 49.75, "day": date(2026, 11, 15)})]
    return Table(columns=COLUMNS, rows=rows, footer=TableRow(values={"name": "الإجمالي", "amount": Decimal("999.00")}, kind="total"))


class TestWorkbook:
    """
    Valid files, registration and modes.
    """

    def test_formatted_file_is_valid_xlsx(self):
        book = export(report(movements()))
        assert book.sheetnames == ["Report"]
        assert book.properties.title == "Excel test"

    def test_registered_as_excel_and_xlsx_without_touching_html(self):
        assert ExporterRegistry.get("excel") is ExcelExporter
        assert ExporterRegistry.get("xlsx") is ExcelExporter
        assert ExporterRegistry.get("html") is HtmlExporter

    def test_html_output_is_unchanged_by_excel_export(self):
        document = report(movements())
        before = HtmlExporter().export(document)
        export(document)
        assert HtmlExporter().export(document) == before

    def test_data_mode_writes_one_sheet_per_table(self):
        book = export(report(KeyValue(label="الفترة", value="2026-11"), movements()), mode="data")
        assert book.sheetnames == ["Report", "Table 1"]
        table = book["Table 1"]
        assert table.freeze_panes == "A2"
        assert table.auto_filter.ref == "A1:C3"
        assert [cell.value for cell in table[1]] == ["البيان / Description", "المبلغ / Amount", "التاريخ / Date"]
        assert [cell.value for cell in book["Report"][1]] == ["الفترة", "2026-11"]

    def test_cell_formats_declare_apply_flags(self):
        import zipfile

        data = ExcelExporter().export(report(movements()), RenderingContext(direction="rtl"))
        styles = zipfile.ZipFile(BytesIO(data)).read("xl/styles.xml").decode("utf-8")
        cell_formats = styles[styles.index("<cellXfs"):styles.index("</cellXfs>")]
        assert cell_formats.count("<xf ") == cell_formats.count('applyFill="1"') == cell_formats.count('applyBorder="1"')

    def test_formatted_mode_cannot_stream(self):
        with pytest.raises(ExcelExportError, match="streaming"):
            ExcelOptions(mode="formatted", streaming=True)

    def test_invalid_options(self):
        for options in ({"mode": "pivot"}, {"sheet_name": "a/b"}, {"sheet_name": "x" * 32}, {"decimal_policy": "round"}):
            with pytest.raises(ExcelExportError):
                ExcelOptions(**options)

    def test_missing_openpyxl_has_clear_message(self):
        with mock.patch.dict(sys.modules, {"openpyxl": None, "reportkit.exporters.excel.workbook": None}), pytest.raises(ImportError, match="pip install"):
            ExcelExporter().export(report(Text(value="x")))


class TestValues:
    """
    Native Excel types and the decimal policy.
    """

    def test_native_types(self):
        columns = [TableColumn(key=key, title=key) for key in ("int", "float", "decimal", "date", "datetime", "bool", "none", "text")]
        values = {"int": 7, "float": 1.5, "decimal": Decimal("12.50"), "date": date(2026, 1, 2), "datetime": datetime(2026, 1, 2, 3, 4), "bool": True, "none": None, "text": "نص"}
        sheet = export(report(Table(columns=columns, rows=[TableRow(values=values)])), mode="data")["Table 1"]
        row = [cell.value for cell in sheet[2]]
        assert row == [7, 1.5, 12.5, datetime(2026, 1, 2), datetime(2026, 1, 2, 3, 4), True, None, "نص"]
        assert [cell.data_type for cell in sheet[2]][:3] == ["n", "n", "n"]

    def test_decimal_within_excel_precision(self):
        sheet = export(report(Table(columns=COLUMNS[:2], rows=[TableRow(values={"name": "x", "amount": Decimal("123456789012.345")})])), mode="data")["Table 1"]
        assert sheet["B2"].value == 123456789012.345

    def test_decimal_beyond_excel_precision_is_explicit(self):
        table = lambda: Table(columns=COLUMNS[:2], rows=[TableRow(values={"name": "x", "amount": Decimal("1234567890.1234567")})])  # noqa: E731
        with pytest.raises(ExcelExportError, match="15 significant digits"):
            export(report(table()), mode="data")
        assert export(report(table()), mode="data", decimal_policy="text")["Table 1"]["B2"].value == "1234567890.1234567"

    def test_unsupported_value_type(self):
        with pytest.raises(ExcelExportError, match="Unsupported value type"):
            export(report(Table(columns=COLUMNS[:1], rows=[TableRow(values={"name": object()})])))

    def test_time_zone_aware_datetime_is_refused(self):
        with pytest.raises(ExcelExportError, match="time zones"):
            export(report(Table(columns=COLUMNS[:1], rows=[TableRow(values={"name": datetime(2026, 1, 1, tzinfo=timezone.utc)})])))

    def test_number_and_date_formats(self):
        sheet = export(report(movements())).active
        amount, day = find(sheet, 150.25), find(sheet, datetime(2026, 11, 14))
        assert amount.number_format == "#,##0.00"
        assert day.number_format == "dd/mm/yyyy"

    def test_formula_injection_is_stored_as_text(self):
        attack = '=HYPERLINK("https://example.com","click")'
        for book in (export(report(Text(value=attack))), export(report(Table(columns=COLUMNS[:1], rows=[TableRow(values={"name": attack})])), mode="data", streaming=True)):
            cell = find(book.worksheets[-1], attack)
            assert cell.data_type == "s"
            assert cell.quotePrefix


class TestTables:
    """
    Headers, prepared footers, spans, styles and laziness.
    """

    def test_header_rows_and_prepared_footer(self):
        sheet = export(report(movements())).active
        assert find(sheet, "البيان\nDescription").font.bold
        assert find(sheet, "دفعة نقدية") and find(sheet, "Bank transfer")
        assert find(sheet, 999).font.bold
        assert sheet.print_title_rows == "$1:$1"

    def test_no_formulas_or_aggregates(self):
        for book in (export(report(movements())), export(report(movements()), mode="data")):
            assert all(cell.data_type != "f" for sheet in book.worksheets for cell in cells(sheet))
            assert any(cell.value == 999 for sheet in book.worksheets for cell in cells(sheet))

    def test_colspan_and_rowspan(self):
        rows = [TableRow(cells=[TableCell(value="ممتد", colspan=2), TableCell(value="tall", rowspan=2)]), TableRow(cells=[TableCell(value="a"), TableCell(value="b")])]
        table = Table(columns=COLUMNS, rows=rows)
        sheet = export(report(table)).active
        wide, tall = merged_range(sheet, "ممتد"), merged_range(sheet, "tall")
        assert (tall.min_row, tall.max_row) == (2, 3) and wide.max_row == 2
        assert wide.max_col + 1 == tall.min_col
        assert merged_range(sheet, "a").max_col < merged_range(sheet, "b").min_col < tall.min_col
        data = export(report(Table(columns=COLUMNS, rows=rows)), mode="data")["Table 1"]
        assert [cell.value for cell in data[2]] == ["ممتد", None, "tall"]
        assert [cell.value for cell in data[3]] == ["a", "b", None]

    def test_overlapping_spans_are_refused(self):
        rows = [TableRow(cells=[TableCell(value="a"), TableCell(value="tall", rowspan=2)]), TableRow(cells=[TableCell(value="wide", colspan=2)])]
        with pytest.raises(ValueError, match="overlaps"):
            export(report(Table(columns=COLUMNS, rows=rows)))

    def test_long_duplicate_table_names_stay_valid(self):
        tables = [Table(columns=COLUMNS[:1], header="ملخص الحركات المالية حسب طريقة الدفع", rows=[]) for _ in range(12)]
        names = export(report(*tables), mode="data").sheetnames
        assert len(set(names)) == 12 and all(len(name) <= 31 for name in names)

    def test_composite_cell_and_multiline_text(self):
        rows = [TableRow(values={"name": TableCell(children=[Text(value="14/11/2026"), Text(value="12:47 AM")]), "amount": "سطر\nثاني"})]
        sheet = export(report(Table(columns=COLUMNS[:2], rows=rows))).active
        assert find(sheet, "14/11/2026\n12:47 AM").alignment.wrap_text
        assert find(sheet, "سطر\nثاني")

    def test_bordered_and_striped_styles(self):
        rows = [TableRow(values={"name": f"row {index}"}) for index in range(3)]
        sheet = export(report(Table(columns=COLUMNS[:1], rows=rows, table_style=TableStyle(bordered=True, striped=True)))).active
        assert find(sheet, "row 0").border.left.style == "thin"
        assert find(sheet, "row 1").fill.fgColor.rgb == "FFF8F8F8"

    def test_streaming_single_use_generator_is_consumed_lazily(self):
        consumed = []

        def rows():
            for index in range(20000):
                consumed.append(index)
                yield TableRow(values={"name": f"row {index}", "amount": index})

        document = report(Table(columns=COLUMNS[:2], rows=rows()))
        assert consumed == []
        sheet = export(document, mode="data", streaming=True)["Table 1"]
        assert len(consumed) == 20000
        assert sheet.max_row == 20001
        assert sheet["A20001"].value == "row 19999" and sheet["B20001"].value == 19999

    def test_row_and_column_limits(self):
        with mock.patch.object(excel_constants, "MAX_ROWS", 3), pytest.raises(ExcelExportError, match="limited"):
            export(report(Table(columns=COLUMNS[:1], rows=(TableRow(values={"name": index}) for index in range(5)))), mode="data", streaming=True)
        with mock.patch.object(excel_constants, "MAX_COLUMNS", 2), pytest.raises(ExcelExportError, match="limited"):
            export(report(movements()), mode="data")


class TestLayout:
    """
    Branding, direction, print settings and unsupported components.
    """

    def test_branding_header_with_logo_and_names(self):
        header = Header(children=[Grid(columns="1fr auto 1fr", children=[Heading(value="فندق الأحقاف", level=2), Image(src=LOGO.as_uri(), width="76"), Heading(value="Alahqaf Hotel", level=2)])])
        sheet = export(report(header, movements())).active
        assert len(sheet._images) == 1
        assert find(sheet, "فندق الأحقاف").font.bold and find(sheet, "Alahqaf Hotel")
        assert find(sheet, "فندق الأحقاف").column < find(sheet, "Alahqaf Hotel").column

    def test_rtl_and_ltr(self):
        rtl, ltr = export(report(Text(value="نص"), Row(children=[KeyValue(label="A", value=1)]))).active, export(report(Text(value="text")), direction="ltr").active
        assert rtl.sheet_view.rightToLeft is True and not ltr.sheet_view.rightToLeft
        rows = [TableRow(values={"name": "x"})]
        for direction, side in (("rtl", "right"), ("ltr", "left")):
            sheet = export(report(Table(columns=[TableColumn(key="name", title="t", align="start")], rows=rows)), direction=direction).active
            assert find(sheet, "x").alignment.horizontal == side

    def test_print_settings_and_page_number(self):
        sheet = export(report(movements(), PageNumber(format="Page {page} of {pages}"), orientation="landscape", margin_top="20mm")).active
        assert sheet.page_setup.orientation == "landscape"
        assert sheet.page_margins.top == pytest.approx(0.787, abs=0.001)
        assert sheet.oddFooter.center.text == "Page &P of &N"
        assert sheet.print_area

    def test_unsupported_components_fail_clearly(self):
        for component in (Chart(), PageCount()):
            for mode in ("formatted", "data"):
                with pytest.raises(ExcelExportError, match="not supported"):
                    export(report(component), mode=mode)

    def test_image_errors(self):
        with pytest.raises(ExcelExportError, match="remote"):
            export(report(Image(src="https://example.com/logo.png")))
        svg = Path(__file__).with_name("logo.svg")
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        try:
            with pytest.raises(ExcelExportError, match="PNG or JPEG"):
                export(report(Image(src=str(svg))))
        finally:
            svg.unlink()

    def test_financial_example_in_both_modes(self):
        from examples.financial_movement.branded import report_builder

        assert export(report_builder().build()).active.max_row > 10
        assert len(export(report_builder().build(), mode="data", streaming=True).sheetnames) == 3
