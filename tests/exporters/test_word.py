import sys
from io import BytesIO
from pathlib import Path
from unittest import mock

import pytest

docx = pytest.importorskip("docx")

import reportkit.exporters.html  # noqa: E402,F401
import reportkit.exporters.word  # noqa: E402,F401  (registers the Word exporter)
from docx.oxml.ns import qn  # noqa: E402
from reportkit.components.document import Header, Page, Report  # noqa: E402
from reportkit.components.layout import Grid  # noqa: E402
from reportkit.components.media import Chart, Image  # noqa: E402
from reportkit.components.pagination import PageNumber  # noqa: E402
from reportkit.components.table import Table, TableCell, TableColumn, TableRow  # noqa: E402
from reportkit.components.typography import Heading, Text  # noqa: E402
from reportkit.exporters.html.exporter import HtmlExporter  # noqa: E402
from reportkit.exporters.registry import ExporterRegistry  # noqa: E402
from reportkit.exporters.word import WordExporter, WordExportError  # noqa: E402
from reportkit.rendering.context import RenderingContext  # noqa: E402

LOGO = Path(__file__).resolve().parents[2] / "examples" / "financial_movement" / "logo.png"
COLUMNS = [TableColumn(key="name", title="البيان", subtitle="Description"), TableColumn(key="amount", title="المبلغ", subtitle="Amount", format="number")]


def report(*children, **page):
    """
    Build a one-page report.
    """
    return Report(title="Word test", children=[Page(children=list(children), **page)])


def export(document, direction="rtl"):
    """
    Export to DOCX and open the result with python-docx.
    """
    data = WordExporter().export(document, RenderingContext(language="ar", direction=direction))
    assert data.startswith(b"PK")
    return docx.Document(BytesIO(data))


def body_xml(document):
    """
    Return the document body XML.
    """
    return document.element.body.xml


def movements(rows=None):
    """
    Return a prepared table with a prepared footer.
    """
    rows = rows if rows is not None else [TableRow(values={"name": "دفعة نقدية", "amount": 150.25}), TableRow(values={"name": "Bank transfer", "amount": 49.75})]
    return Table(columns=COLUMNS, rows=rows, footer=TableRow(values={"name": "الإجمالي", "amount": 999}, kind="total"))


def test_valid_docx_and_registration():
    document = export(report(Text(value="مرحبا Hello")))
    assert document.core_properties.title == "Word test"
    assert ExporterRegistry.get("word") is WordExporter and ExporterRegistry.get("docx") is WordExporter


def test_html_output_is_unchanged():
    document = report(movements())
    before = HtmlExporter().export(document)
    export(document)
    assert HtmlExporter().export(document) == before


def test_rtl_paragraphs_and_tables():
    xml = body_xml(export(report(Text(value="تقرير"), movements())))
    assert "<w:bidi/>" in xml and "<w:bidiVisual/>" in xml and "<w:rtl/>" in xml


def test_ltr_has_no_bidi():
    xml = body_xml(export(report(Text(value="Report"), movements()), direction="ltr"))
    assert "<w:bidi/>" not in xml and "<w:bidiVisual/>" not in xml


def test_dates_and_numbers_stay_left_to_right():
    paragraph = export(report(Text(value="20/11/2026"))).paragraphs[0]
    assert paragraph.text == "20/11/2026"
    assert paragraph.runs[0]._r.find(qn("w:rPr")).find(qn("w:rtl")) is None


def test_table_header_footer_and_formatting():
    table = export(report(movements())).tables[0]
    assert table.rows[0].cells[0].text == "البيان\nDescription"
    assert table.rows[0]._tr.trPr.find(qn("w:tblHeader")) is not None
    assert [cell.text for cell in table.rows[1].cells] == ["دفعة نقدية", "150.25"]
    assert table.rows[-1].cells[1].text == "999.00"


def test_colspan_and_rowspan():
    rows = [TableRow(cells=[TableCell(value="wide", colspan=2)]), TableRow(cells=[TableCell(value="tall", rowspan=2), TableCell(value="b")]), TableRow(cells=[TableCell(value="c")])]
    xml = body_xml(export(report(Table(columns=COLUMNS, rows=rows))))
    assert '<w:gridSpan w:val="2"/>' in xml and '<w:vMerge w:val="restart"/>' in xml


def test_overlapping_spans_are_refused():
    rows = [TableRow(cells=[TableCell(value="a"), TableCell(value="tall", rowspan=2)]), TableRow(cells=[TableCell(value="wide", colspan=2)])]
    with pytest.raises(ValueError, match="overlaps"):
        export(report(Table(columns=COLUMNS, rows=rows)))


def test_composite_cells():
    rows = [TableRow(values={"name": TableCell(children=[Text(value="14/11/2026"), Text(value="12:47 AM")]), "amount": 1})]
    assert export(report(Table(columns=COLUMNS, rows=rows))).tables[0].rows[1].cells[0].text == "14/11/2026\n12:47 AM"


def test_rows_are_consumed_lazily():
    consumed = []

    def rows():
        for index in range(200):
            consumed.append(index)
            yield TableRow(values={"name": f"row {index}", "amount": index})

    document = report(Table(columns=COLUMNS, rows=rows()))
    assert consumed == []
    assert len(export(document).tables[0].rows) == 201 and len(consumed) == 200


def test_large_table_rows_are_spooled_in_order():
    rows = (TableRow(values={"name": f"row {index}", "amount": index}) for index in range(1500))
    table = export(report(Text(value="before"), movements(rows), Text(value="after"))).tables[0]
    texts = [row.cells[0].text for row in table.rows]
    assert texts[0] == "البيان\nDescription" and texts[-1] == "الإجمالي"
    assert texts[1:-1] == [f"row {index}" for index in range(1500)]


def test_row_spans_across_spooled_rows():
    rows = [TableRow(values={"name": f"row {index}", "amount": index}) for index in range(450)]
    rows[199] = TableRow(cells=[TableCell(value="tall", rowspan=3), TableCell(value="b")])
    rows[200] = TableRow(cells=[TableCell(value="c")])
    rows[201] = TableRow(cells=[TableCell(value="d")])
    table = export(report(movements(rows))).tables[0]
    assert len(table.rows) == 452
    assert [table.rows[number].cells[0].text for number in (200, 201, 202)] == ["tall"] * 3
    assert table.rows[202].cells[1].text == "d" and table.rows[203].cells[0].text == "row 202"


def test_export_to_path_and_stream(tmp_path):
    document = report(movements((TableRow(values={"name": f"row {index}", "amount": index}) for index in range(300))))
    path = tmp_path / "report.docx"
    WordExporter().export_to(document, path)
    assert len(docx.Document(path).tables[0].rows) == 302
    stream = BytesIO()
    WordExporter().export_to(report(movements()), stream)
    assert stream.getvalue().startswith(b"PK")


def test_page_settings_and_page_numbers():
    document = export(report(Text(value="x"), PageNumber(format="Page {page} of {pages}"), orientation="landscape", margin_top="20mm", page_number_position="bottom-center"))
    section = document.sections[0]
    assert (round(section.page_width.mm), round(section.page_height.mm), round(section.top_margin.mm)) == (297, 210, 20)
    footer = section.footer._element.xml
    assert 'w:instr="PAGE"' in footer and 'w:instr="NUMPAGES"' in footer


def test_repeated_header_goes_to_page_header():
    document = export(report(Header(repeat=True, children=[Text(value="Running header")]), Text(value="Body")))
    assert "Running header" in document.sections[0].header._element.xml
    assert "Running header" not in body_xml(document)


def test_branding_grid_with_logo():
    header = Grid(columns="1fr auto 1fr", children=[Heading(value="فندق الأحقاف", level=2), Image(src=LOGO.as_uri(), width="76"), Heading(value="Alahqaf Hotel", level=2)])
    document = export(report(header))
    assert len(document.inline_shapes) == 1
    assert [cell.text for cell in document.tables[0].rows[0].cells] == ["فندق الأحقاف", "", "Alahqaf Hotel"]


def test_unsupported_components_and_images():
    with pytest.raises(WordExportError, match="not supported"):
        export(report(Chart()))
    with pytest.raises(WordExportError, match="remote"):
        export(report(Image(src="https://example.com/logo.png")))


def test_missing_python_docx_has_clear_message():
    with mock.patch.dict(sys.modules, {"docx": None, "reportkit.exporters.word.document": None}), pytest.raises(ImportError, match="pip install"):
        WordExporter().export(report(Text(value="x")))


def test_financial_example():
    from examples.financial_movement.branded import report_builder

    document = export(report_builder().build())
    assert len(document.tables) > 3 and len(document.inline_shapes) == 1
