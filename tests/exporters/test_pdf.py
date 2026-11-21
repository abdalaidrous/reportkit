import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import reportkit.exporters.html  # noqa: F401  (registers the HTML renderers)
from reportkit.components.document import Footer, Header, Page, Report
from reportkit.components.media import Image
from reportkit.components.pagination import PageNumber
from reportkit.components.table import Table, TableCell, TableColumn, TableRow
from reportkit.components.typography import Text
from reportkit.exporters.html.exporter import HtmlExporter
from reportkit.exporters.pdf import PdfExporter, PdfExportError, is_allowed_resource, resolve_root
from reportkit.exporters.registry import ExporterRegistry
from reportkit.rendering.context import RenderingContext
from reportkit.styles.style import Style

ROOT = Path(__file__).resolve().parents[2]
LOGO = ROOT / "examples" / "financial_movement" / "logo.png"
BROKEN_IMAGE = "data:image/png;base64,bm90IGFuIGltYWdl"
PIXEL = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
MM = 96 / 25.4


def weasyprint_available():
    """
    Return True when WeasyPrint and its system libraries can be imported.
    """
    try:
        PdfExporter.load_weasyprint()
    except ImportError:
        return False
    return True


def report(*children, **page):
    """
    Build a one-page report with the given children and page settings.
    """
    return Report(title="PDF test", children=[Page(children=list(children), **page)])


def layout(document, direction="rtl"):
    """
    Lay a report out with WeasyPrint and return the rendered document.
    """
    html = HtmlExporter().export(document, RenderingContext(language="ar", direction=direction)).decode("utf-8")
    return PdfExporter.render(html)


def page_text(page):
    """
    Collect the text laid out on one page, margin boxes included.
    """
    return " ".join(box.text for box in page._page_box.descendants() if hasattr(box, "text"))


class PdfExporterWithoutWeasyPrintTests(unittest.TestCase):
    """
    Behaviour that does not need WeasyPrint installed.
    """

    def test_missing_weasyprint_has_clear_message(self):
        with mock.patch.dict(sys.modules, {"weasyprint": None}), self.assertRaises(ImportError) as caught:
            PdfExporter.export(report(Text(value="x")))
        self.assertIn("pip install", str(caught.exception))
        self.assertIsNotNone(caught.exception.__cause__)

    def test_registered_as_pdf(self):
        self.assertIs(ExporterRegistry.get("pdf"), PdfExporter)

    def test_missing_local_image_fails_before_conversion(self):
        with self.assertRaises(FileNotFoundError):
            PdfExporter.export(report(Image(src=str(ROOT / "missing.png"))))

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve() / "assets"
        self.root.mkdir()
        self.inside = self.root / "logo file.png"
        self.inside.write_bytes(b"png")
        self.outside = self.root.parent / "secret.png"
        self.outside.write_bytes(b"png")

    def test_data_uri_is_always_allowed(self):
        self.assertTrue(is_allowed_resource(PIXEL, None))
        self.assertTrue(is_allowed_resource(PIXEL, self.root))

    def test_file_inside_base_url_is_allowed(self):
        self.assertTrue(is_allowed_resource(self.inside.as_uri(), self.root))  # Percent-encoded space.
        self.assertTrue(is_allowed_resource("file://localhost" + self.inside.as_uri()[len("file://"):], self.root))

    def test_files_need_a_base_url(self):
        self.assertFalse(is_allowed_resource(self.inside.as_uri(), None))

    def test_file_outside_base_url_is_refused(self):
        self.assertFalse(is_allowed_resource(self.outside.as_uri(), self.root))
        self.assertFalse(is_allowed_resource((self.root / ".." / "secret.png").as_uri(), self.root))

    def test_missing_files_and_folders_are_refused(self):
        self.assertFalse(is_allowed_resource((self.root / "missing.png").as_uri(), self.root))
        self.assertFalse(is_allowed_resource(self.root.as_uri(), self.root))

    def test_network_and_remote_hosts_are_refused(self):
        self.assertFalse(is_allowed_resource("https://example.com/logo.png", self.root))
        self.assertFalse(is_allowed_resource("file://server/share/logo.png", self.root))

    def test_symlink_escaping_base_url_is_refused(self):
        link = self.root / "link.png"
        try:
            os.symlink(self.outside, link)
        except (OSError, NotImplementedError):
            self.skipTest("Creating symlinks is not permitted here")
        self.assertFalse(is_allowed_resource(link.as_uri(), self.root))

    def test_base_url_must_be_an_existing_folder(self):
        self.assertEqual(resolve_root(self.root.as_uri()), self.root)
        self.assertEqual(resolve_root(str(self.root)), self.root)
        with self.assertRaises(ValueError):
            resolve_root(self.root / "missing")
        with self.assertRaises(ValueError):
            resolve_root(self.inside)


@unittest.skipUnless(weasyprint_available(), "WeasyPrint or its system libraries are not installed")
class PdfExporterTests(unittest.TestCase):
    """
    End-to-end PDF export through WeasyPrint.
    """

    def test_returns_pdf_bytes(self):
        pdf = PdfExporter.export(report(Text(value="Hello")))
        self.assertIsInstance(pdf, bytes)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_financial_example(self):
        from examples.financial_movement.report import build_report

        pdf = PdfExporter.export(build_report(), RenderingContext(language="ar", direction="rtl"))
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_arabic_and_english_text(self):
        document = report(Text(value="تقرير الحركة المالية"), Text(value="Financial Movement Report"))
        text = page_text(layout(document).pages[0])
        self.assertIn("Financial Movement Report", text)
        self.assertIn("تقرير", text)
        self.assertIn(b"/Length1", PdfExporter.export(document))  # Embedded font programs carry Length1.

    def test_local_and_embedded_images(self):
        pdf = PdfExporter.export(report(Image(src=LOGO.as_uri(), width="40"), Image(src=PIXEL, width="10")))
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertIn(b"/Image", pdf)

    def test_page_size_orientation_and_margins(self):
        document = layout(report(Text(value="x"), size="A4", orientation="landscape", margin_top="20mm", margin_left="10mm"))
        page = document.pages[0]
        self.assertAlmostEqual(page.width, 297 * MM, delta=1)
        self.assertAlmostEqual(page.height, 210 * MM, delta=1)
        self.assertAlmostEqual(page._page_box.margin_top, 20 * MM, delta=1)
        self.assertAlmostEqual(page._page_box.margin_left, 10 * MM, delta=1)

    def test_running_header_footer_and_page_numbers(self):
        rows = [TableRow(values={"a": f"row {index}"}) for index in range(120)]
        document = layout(report(
            Header(repeat=True, children=[Text(value="Running header")]),
            Footer(repeat=True, children=[Text(value="Running footer")]),
            Table(columns=[TableColumn(key="a", title="Column title")], rows=rows),
            PageNumber(format="Page {page} of {pages}"),
            page_number_position="bottom-right",
        ))
        self.assertGreater(len(document.pages), 1)
        last = len(document.pages)
        for number, page in enumerate(document.pages, start=1):
            text = page_text(page)
            self.assertIn(f"Page {number} of {last}", text)
            self.assertIn("Running header", text)
            self.assertIn("Running footer", text)

    def test_long_table_repeats_header(self):
        rows = [TableRow(values={"a": f"row {index}", "b": "قيمة"}) for index in range(150)]
        document = layout(report(Table(columns=[TableColumn(key="a", title="Column title"), TableColumn(key="b", title="عنوان")], rows=rows)))
        self.assertGreater(len(document.pages), 1)
        for page in document.pages:
            self.assertIn("Column title", page_text(page))

    def test_composite_cells(self):
        cell = TableCell(children=[Text(value="2026-11-21"), Text(value="10:30 AM", style=Style(font_size=9, color="#777777"))])
        document = layout(report(Table(columns=[TableColumn(key="date", title="Date")], rows=[TableRow(values={"date": cell})])))
        text = page_text(document.pages[0])
        self.assertIn("2026-11-21", text)
        self.assertIn("10:30 AM", text)

    def test_remote_resource_is_refused(self):
        with self.assertRaises(PdfExportError) as caught:
            PdfExporter.export(report(Image(src="https://example.com/logo.png")))
        self.assertIn("https://example.com/logo.png", str(caught.exception))
        self.assertIsNotNone(caught.exception.__cause__)

    def test_file_inside_base_url_is_embedded(self):
        html = '<html><body><img src="' + LOGO.as_uri() + '"></body></html>'
        pdf = PdfExporter.convert(html, base_url=LOGO.parent)
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertIn(b"/Image", pdf)

    def test_relative_file_inside_base_url_is_embedded(self):
        self.assertIn(b"/Image", PdfExporter.convert('<html><body><img src="logo.png"></body></html>', base_url=LOGO.parent))

    def test_file_without_base_url_is_refused(self):
        with self.assertRaises(PdfExportError) as caught:
            PdfExporter.convert('<html><body><img src="' + LOGO.as_uri() + '"></body></html>')
        self.assertIn(LOGO.as_uri(), str(caught.exception))

    def test_file_outside_base_url_is_refused(self):
        with self.assertRaises(PdfExportError):
            PdfExporter.convert('<html><body><img src="' + LOGO.as_uri() + '"></body></html>', base_url=ROOT / "tests")

    def test_broken_resource_is_not_skipped_silently(self):
        with self.assertRaises(PdfExportError) as caught:
            PdfExporter.export(report(Image(src=BROKEN_IMAGE)))
        self.assertIn("skipped resources", str(caught.exception))

    def test_relative_url_without_base_url_is_reported(self):
        with self.assertRaises(PdfExportError):
            PdfExporter.convert('<html><body><img src="logo.png"></body></html>')

if __name__ == "__main__":
    unittest.main()
