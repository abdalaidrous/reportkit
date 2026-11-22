"""
QRCode, Chart and PageCount across the exporters, and ExcelExporter.export_to.
"""
import io
import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

pytest.importorskip("segno")

import reportkit.exporters.html  # noqa: E402,F401  (registers the HTML renderers)
from reportkit.builders import ReportBuilder  # noqa: E402
from reportkit.components.document import Footer, Page, Report  # noqa: E402
from reportkit.components.media import Chart, ChartSeries, QRCode  # noqa: E402
from reportkit.components.pagination import PageCount, PageNumber  # noqa: E402
from reportkit.components.table import Table, TableColumn, TableRow  # noqa: E402
from reportkit.components.typography import Text  # noqa: E402
from reportkit.core.serializer import ComponentSerializer  # noqa: E402
from reportkit.exporters.html.exporter import HtmlExporter  # noqa: E402
from reportkit.rendering.context import RenderingContext  # noqa: E402

from .test_pdf import weasyprint_available  # noqa: E402


def installed(module):
    """
    Return whether an optional module can be imported.
    """
    try:
        __import__(module)
    except ImportError:
        return False
    return True


CONTEXT = RenderingContext(language="ar", direction="rtl")
URL = "https://example.com/inv/1001"


def report(*children):
    """
    Build a one-page report.
    """
    return Report(title="Media", children=[Page(children=list(children))])


def html(*children):
    """
    Export a one-page report to HTML text.
    """
    return HtmlExporter().export(report(*children), CONTEXT).decode("utf-8")


def revenue(**options):
    """
    A two-series chart with a negative value.
    """
    series = [ChartSeries(name="2025", values=[Decimal("1200.50"), 3400, -800]), ChartSeries(name="2026", values=[2000, 1500, 900], color="#123456")]
    return Chart(title="الإيرادات", labels=["يناير", "فبراير", "مارس"], series=series, **options)


class TestValidation:

    def test_page_count_needs_exactly_one_total(self):
        assert PageCount(format="عدد الصفحات: {pages}").parts == ("عدد الصفحات: ", "")
        for invalid in ("pages", "{pages} {pages}", "{page} / {pages}"):
            with pytest.raises(ValueError):
                PageCount(format=invalid)
        with pytest.raises(TypeError):
            PageCount(format=3)

    def test_qr_code_rules(self):
        assert QRCode(value=URL).size == 96
        for options in ({"value": ""}, {"value": URL, "size": 0}, {"value": URL, "size": True}, {"value": URL, "error_correction": "X"}, {"value": URL, "quiet_zone": 11}):
            with pytest.raises(ValueError):
                QRCode(**options)

    def test_chart_rules(self):
        assert revenue().series[1].color == "#123456"
        with pytest.raises(ValueError, match="one value per label"):
            Chart(labels=["a", "b"], series=[ChartSeries(name="s", values=[1])])
        with pytest.raises(ValueError, match="finite"):
            Chart(labels=["a"], series=[ChartSeries(name="s", values=[float("nan")])])
        with pytest.raises(ValueError, match="exactly one series"):
            Chart(chart_type="pie", labels=["a"], series=[ChartSeries(name="s", values=[1]), ChartSeries(name="t", values=[1])])
        with pytest.raises(ValueError, match="non-negative"):
            Chart(chart_type="pie", labels=["a", "b"], series=[ChartSeries(name="s", values=[1, -1])])
        with pytest.raises(ValueError, match="hex color"):
            Chart(labels=["a"], series=[ChartSeries(name="s", values=[1], color="red")])
        with pytest.raises(ValueError, match="Chart type"):
            Chart(chart_type="radar", labels=["a"], series=[ChartSeries(name="s", values=[1])])

    def test_chart_round_trips_through_a_dictionary(self):
        chart = ComponentSerializer.from_dict(ComponentSerializer.to_dict(revenue()))
        assert chart == revenue()


class TestHtml:

    def test_page_count_is_hidden_text_around_a_counter(self):
        output = html(PageCount(format="Total pages: {pages}"))
        assert '<p class="rk-text rk-page-count" data-rk-page-count="Total pages: {pages}"><span class="rk-page-count__text" dir="ltr">Total pages: <span class="rk-page-count__value"></span></span></p>' in output
        assert "rk-page-count--deferred" not in output

    def test_qr_code_is_an_svg_image_of_the_declared_size(self):
        output = html(QRCode(value=URL, size=80, alt="Invoice <1001>"))
        assert 'src="data:image/svg+xml' in output
        assert 'width="80" height="80"' in output
        assert 'alt="Invoice &lt;1001&gt;"' in output

    def test_bar_chart_draws_bars_and_html_labels(self):
        output = html(revenue(show_values=True))
        assert output.count("<rect ") == 6
        assert 'fill="#123456"' in output
        assert '<span class="rk-chart__label rk-chart__label--label" dir="rtl"' in output and ">يناير</span>" in output
        assert ">-800</span>" in output and ">1,200</span>" in output
        assert '<figcaption class="rk-chart__title">الإيرادات</figcaption>' in output

    def test_chart_texts_are_escaped(self):
        output = html(Chart(labels=["<b>a</b>"], series=[ChartSeries(name="<i>s</i>", values=[1])]))
        assert "&lt;b&gt;a&lt;/b&gt;" in output and "&lt;i&gt;s&lt;/i&gt;" in output
        assert "<b>a</b>" not in output

    def test_line_and_pie_charts(self):
        line = html(Chart(chart_type="line", labels=["a", "b", "c"], series=[ChartSeries(name="s", values=[1, 2.5, 2])], decimals=1))
        assert line.count("<polyline ") == 1 and line.count("<circle ") == 3
        pie = html(Chart(chart_type="pie", labels=["a", "b"], series=[ChartSeries(name="s", values=[75, 25])], show_values=True))
        assert pie.count("<path ") == 2 and ">75%</span>" in pie and ">25%</span>" in pie
        whole = html(Chart(chart_type="pie", labels=["a", "b"], series=[ChartSeries(name="s", values=[10, 0])], legend=False))
        assert whole.count("<path ") == 1 and "<ul class=\"rk-chart__legend\"" not in whole


class TestBuilder:

    def test_builder_adds_the_new_components_in_order(self):
        built = ReportBuilder("B").qr_code(URL, size=64).chart(["a"], [ChartSeries(name="s", values=[1])], chart_type="line", title="T").page_count("{pages} pages").build()
        qr, chart, count = built.children[0].children
        assert (qr.value, qr.size, chart.chart_type, chart.title, count.format) == (URL, 64, "line", "T", "{pages} pages")


@pytest.mark.skipif(not installed("openpyxl"), reason="openpyxl is not installed")
class TestExcel:

    @property
    def openpyxl(self):
        import openpyxl

        return openpyxl

    def export(self, document, **options):
        """
        Export to XLSX bytes with the given options.
        """
        import reportkit.exporters.excel  # noqa: F401
        from reportkit.exporters.excel import ExcelExporter, ExcelOptions

        return ExcelExporter().export(document, CONTEXT, ExcelOptions(**options))

    def test_export_to_a_path_and_a_stream_matches_export(self):
        import reportkit.exporters.excel  # noqa: F401
        from reportkit.exporters.excel import ExcelExporter, ExcelOptions

        document = report(Text(value="x"), Table(columns=[TableColumn(key="a", title="A")], rows=[TableRow(values={"a": 1})]))
        stream = io.BytesIO()
        ExcelExporter().export_to(document, stream, CONTEXT, ExcelOptions(mode="data", streaming=True))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "report.xlsx"
            ExcelExporter().export_to(document, path, CONTEXT)
            assert self.openpyxl.load_workbook(path).active["A1"].value == "x"
        assert self.openpyxl.load_workbook(stream).worksheets[1]["A2"].value == 1

    def test_builder_export_to_streams_excel(self):
        stream = ReportBuilder("B").add(Text(value="x")).export_to("xlsx", io.BytesIO(), CONTEXT)
        assert stream.getvalue().startswith(b"PK")

    def test_formatted_chart_reads_a_hidden_data_sheet(self):
        book = self.openpyxl.load_workbook(io.BytesIO(self.export(report(revenue()))))
        assert book.sheetnames == ["Report", "Chart data"] and book["Chart data"].sheet_state == "hidden"
        assert [cell.value for cell in book["Chart data"][2]] == ["يناير", 1200.5, 2000]
        assert len(book["Report"]._charts) == 1

    def test_data_chart_gets_its_own_sheet_with_the_chart(self):
        book = self.openpyxl.load_workbook(io.BytesIO(self.export(report(revenue()), mode="data", streaming=True)))
        sheet = book["الإيرادات"]
        assert [cell.value for cell in sheet[1]] == [None, "2025", "2026"]
        assert len(sheet._charts) == 1

    def test_qr_code_is_an_image(self):
        sheet = self.openpyxl.load_workbook(io.BytesIO(self.export(report(QRCode(value=URL))))).active
        assert len(sheet._images) == 1


@pytest.mark.skipif(not installed("docx"), reason="python-docx is not installed")
class TestWord:

    @property
    def docx(self):
        import docx

        return docx

    def export(self, document):
        """
        Export to DOCX and open it with python-docx.
        """
        import reportkit.exporters.word  # noqa: F401
        from reportkit.exporters.word import WordExporter

        return self.docx.Document(io.BytesIO(WordExporter().export(document, CONTEXT)))

    def test_page_count_is_a_numpages_field(self):
        document = self.export(report(Footer(repeat=True, children=[PageCount(format="من {pages}")]), Text(value="x")))
        footer = document.sections[0].footer._element.xml
        assert 'w:instr="NUMPAGES"' in footer and "من " in footer

    def test_chart_is_a_table_of_its_values(self):
        document = self.export(report(revenue(decimals=2)))
        table = document.tables[0]
        assert [cell.text for cell in table.rows[-1].cells] == ["مارس", "-800.00", "900.00"]

    def test_qr_code_is_a_picture(self):
        assert len(self.export(report(QRCode(value=URL))).inline_shapes) == 1


@pytest.mark.skipif(not weasyprint_available(), reason="WeasyPrint is not installed")
class TestPdf:

    def numbered(self, rows):
        """
        A report with page counts in the content and in a repeating footer, over a long table.
        """
        table = Table(columns=[TableColumn(key="a", title="A")], rows=[TableRow(values={"a": f"row {index}"}) for index in range(rows)])
        footer = Footer(repeat=True, children=[PageCount(format="of {pages}")])
        return Report(title="Count", children=[Page(children=[footer, PageCount(format="Total pages: {pages}"), table, PageNumber(format="{page}")])])

    def texts(self, pdf):
        """
        Return the text of every page.
        """
        pypdf = pytest.importorskip("pypdf")
        return [page.extract_text() for page in pypdf.PdfReader(io.BytesIO(pdf)).pages]

    @pytest.mark.parametrize("options", [{"chunk_rows": None}, {"chunk_rows": 60}, {"chunk_rows": 60, "workers": 2}])
    def test_page_count_shows_the_merged_total(self, options):
        from reportkit.exporters.pdf import PdfExporter, PdfOptions

        texts = self.texts(PdfExporter.export(self.numbered(250), CONTEXT, options=PdfOptions(**options)))
        total = len(texts)
        assert total > 3
        assert f"Total pages: {total}" in texts[0]
        assert all(f"of {total}" in text for text in texts)

    def test_qr_code_and_chart_lay_out(self):
        from reportkit.exporters.pdf import PdfExporter

        pdf = PdfExporter.export(report(QRCode(value=URL), revenue(show_values=True)), CONTEXT)
        assert pdf.startswith(b"%PDF")
        assert "3,400" in self.texts(pdf)[0]
