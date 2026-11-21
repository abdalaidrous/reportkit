import logging
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import reportkit.exporters.html  # noqa: F401  (registers the HTML renderers)
from reportkit.components.document import Footer, Header, Page, Report
from reportkit.components.layout import Grid, Row
from reportkit.components.media import Image
from reportkit.components.pagination import PageNumber
from reportkit.components.table import Table, TableCell, TableColumn, TableRow
from reportkit.components.typography import Text
from reportkit.exporters.html.exporter import HtmlExporter
from reportkit.exporters.pdf import PdfConversionService, PdfExporter, PdfExportError
from reportkit.exporters.pdf.conversion import WeasyPrintErrorMonitor
from reportkit.exporters.pdf.dependencies import load_weasyprint
from reportkit.exporters.pdf.resources import PdfResourcePolicy
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
        load_weasyprint()
    except ImportError:
        return False
    return True


def allowed(url, root):
    """
    Return whether the resource policy for root allows url.
    """
    return PdfResourcePolicy(root).is_allowed(url)


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
    return PdfConversionService.render(html)


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
        self.assertTrue(allowed(PIXEL, None))
        self.assertTrue(allowed(PIXEL, self.root))

    def test_file_inside_base_url_is_allowed(self):
        self.assertTrue(allowed(self.inside.as_uri(), self.root))  # Percent-encoded space.
        self.assertTrue(allowed("file://localhost" + self.inside.as_uri()[len("file://"):], self.root))

    def test_files_need_a_base_url(self):
        self.assertFalse(allowed(self.inside.as_uri(), None))

    def test_file_outside_base_url_is_refused(self):
        self.assertFalse(allowed(self.outside.as_uri(), self.root))
        self.assertFalse(allowed((self.root / ".." / "secret.png").as_uri(), self.root))

    def test_missing_files_and_folders_are_refused(self):
        self.assertFalse(allowed((self.root / "missing.png").as_uri(), self.root))
        self.assertFalse(allowed(self.root.as_uri(), self.root))

    def test_network_and_remote_hosts_are_refused(self):
        self.assertFalse(allowed("https://example.com/logo.png", self.root))
        self.assertFalse(allowed("file://server/share/logo.png", self.root))

    def test_symlink_escaping_base_url_is_refused(self):
        link = self.root / "link.png"
        try:
            os.symlink(self.outside, link)
        except (OSError, NotImplementedError):
            self.skipTest("Creating symlinks is not permitted here")
        self.assertFalse(allowed(link.as_uri(), self.root))

    def test_base_url_must_be_an_existing_folder(self):
        self.assertEqual(PdfResourcePolicy.resolve_root(self.root.as_uri()), self.root)
        self.assertEqual(PdfResourcePolicy.resolve_root(str(self.root)), self.root)
        with self.assertRaises(ValueError):
            PdfResourcePolicy.resolve_root(self.root / "missing")
        with self.assertRaises(ValueError):
            PdfResourcePolicy.resolve_root(self.inside)


class WeasyPrintErrorMonitorTests(unittest.TestCase):
    """
    Log monitoring must stay per conversion when reports are exported concurrently.
    """

    def test_collects_only_errors_from_its_own_thread(self):
        logger = logging.getLogger("weasyprint")
        with WeasyPrintErrorMonitor() as monitor:
            other = threading.Thread(target=lambda: logger.error("other report failed"))
            other.start()
            other.join()
            logger.error("own report failed")
        self.assertEqual(monitor.messages, ["own report failed"])

    def test_raises_for_collected_errors(self):
        with WeasyPrintErrorMonitor() as monitor:
            logging.getLogger("weasyprint").error("image skipped")
        with self.assertRaises(PdfExportError):
            monitor.raise_for_errors()

    def test_stops_listening_after_exit(self):
        with WeasyPrintErrorMonitor() as monitor:
            pass
        logging.getLogger("weasyprint").error("later")
        self.assertEqual(monitor.messages, [])


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

    def test_rtl_grid_keeps_reading_order(self):
        grid = Grid(columns="1fr 1fr 1fr", children=[Text(value="FIRST"), Text(value="SECOND"), Text(value="THIRD")])
        boxes = {box.text.strip(): box.position_x for box in layout(report(grid)).pages[0]._page_box.descendants() if hasattr(box, "text") and box.text.strip()}
        self.assertGreater(boxes["FIRST"], boxes["SECOND"])
        self.assertGreater(boxes["SECOND"], boxes["THIRD"])

    def test_flex_row_items_are_not_squeezed(self):
        row = Row(justify="space-between", children=[Text(value="الرقم الضريبي"), Text(value="2552977145"), Text(value="VAT No")])
        texts = [box.text.strip() for box in layout(report(row)).pages[0]._page_box.descendants() if hasattr(box, "text") and box.text.strip()]
        self.assertIn("الرقم الضريبي", texts)
        self.assertIn("VAT No", texts)

    def test_long_financial_report_with_composite_cells(self):
        from examples.financial_movement import report as example

        with mock.patch.object(example, "MOVEMENTS", example.MOVEMENTS * 12):
            document = example.build_report()
        html = HtmlExporter().export(document, RenderingContext(language="ar", direction="rtl")).decode("utf-8")
        pages = PdfConversionService.render(html).pages
        self.assertGreater(len(pages), 1)
        for number, page in enumerate(pages, start=1):
            text = page_text(page)
            self.assertIn("Voucher No.", text)
            self.assertIn(f"Page {number} of {len(pages)}", text)
        self.assertIn("12:47 AM", page_text(pages[0]))

    def test_concurrent_exports_keep_errors_separate(self):
        documents = [report(Text(value=f"Report {index}"), Image(src=PIXEL, width="10")) for index in range(6)]
        documents[2] = report(Text(value="Broken"), Image(src=BROKEN_IMAGE))

        def export(document):
            try:
                return PdfExporter.export(document)
            except PdfExportError as error:
                return error

        with ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(export, documents))
        self.assertIsInstance(results[2], PdfExportError)
        for index, result in enumerate(results):
            if index != 2:
                self.assertIsInstance(result, bytes, f"report {index} failed: {result}")
                self.assertTrue(result.startswith(b"%PDF"))

    def test_remote_resource_is_refused(self):
        with self.assertRaises(PdfExportError) as caught:
            PdfExporter.export(report(Image(src="https://example.com/logo.png")))
        self.assertIn("https://example.com/logo.png", str(caught.exception))
        self.assertIsNotNone(caught.exception.__cause__)

    def test_file_inside_base_url_is_embedded(self):
        html = '<html><body><img src="' + LOGO.as_uri() + '"></body></html>'
        pdf = PdfConversionService.convert(html, base_url=LOGO.parent)
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertIn(b"/Image", pdf)

    def test_relative_file_inside_base_url_is_embedded(self):
        self.assertIn(b"/Image", PdfConversionService.convert('<html><body><img src="logo.png"></body></html>', base_url=LOGO.parent))

    def test_file_without_base_url_is_refused(self):
        with self.assertRaises(PdfExportError) as caught:
            PdfConversionService.convert('<html><body><img src="' + LOGO.as_uri() + '"></body></html>')
        self.assertIn(LOGO.as_uri(), str(caught.exception))

    def test_file_outside_base_url_is_refused(self):
        with self.assertRaises(PdfExportError):
            PdfConversionService.convert('<html><body><img src="' + LOGO.as_uri() + '"></body></html>', base_url=ROOT / "tests")

    def test_broken_resource_is_not_skipped_silently(self):
        with self.assertRaises(PdfExportError) as caught:
            PdfExporter.export(report(Image(src=BROKEN_IMAGE)))
        self.assertIn("skipped resources", str(caught.exception))

    def test_relative_url_without_base_url_is_reported(self):
        with self.assertRaises(PdfExportError):
            PdfConversionService.convert('<html><body><img src="logo.png"></body></html>')

if __name__ == "__main__":
    unittest.main()
