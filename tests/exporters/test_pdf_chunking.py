import io
import tempfile
import unittest
from pathlib import Path

import reportkit.exporters.html  # noqa: F401  (registers the HTML renderers)
from reportkit.components.document import Footer, Header, Page, Report
from reportkit.components.pagination import PageNumber
from reportkit.components.table import Table, TableColumn, TableRow, TableStyle
from reportkit.components.typography import Text
from reportkit.exporters.html.page import HtmlPageResolver
from reportkit.exporters.pdf import PdfExporter, PdfExportError, PdfOptions
from reportkit.exporters.pdf.chunking import TableFragment
from reportkit.exporters.pdf.chunking.flow import ReportFlow, RowStream
from reportkit.exporters.pdf.chunking.planner import ChunkPlanner

from .test_pdf import weasyprint_available


def counted_rows(count, read):
    """
    Yield rows lazily, recording how many were read.
    """
    for index in range(count):
        read.append(index)
        yield TableRow(values={"a": f"row {index}", "b": "قيمة"})


def table(rows, **options):
    """
    Build a two-column table over the given rows.
    """
    return Table(columns=[TableColumn(key="a", title="Column title"), TableColumn(key="b", title="عنوان")], rows=rows, **options)


def report(*children):
    """
    Build a one-page report with numbered pages.
    """
    return Report(title="Chunked", children=[Page(children=[*children, PageNumber(format="Page {page} of {pages}")])])


class PdfOptionsTests(unittest.TestCase):

    def test_chunk_rows_must_be_positive_or_none(self):
        self.assertIsNone(PdfOptions(chunk_rows=None).chunk_rows)
        for invalid in (0, -1, 2.5, True, "10"):
            with self.assertRaises(PdfExportError):
                PdfOptions(chunk_rows=invalid)

    def test_workers_must_be_positive_and_need_chunks(self):
        self.assertEqual(PdfOptions(workers=4).workers, 4)
        for invalid in (0, -2, 1.5, True):
            with self.assertRaises(PdfExportError):
                PdfOptions(workers=invalid)
        with self.assertRaises(PdfExportError):
            PdfOptions(chunk_rows=None, workers=2)


class RowStreamTests(unittest.TestCase):

    def test_peek_reads_only_what_is_needed(self):
        read = []
        stream = RowStream(table(counted_rows(100, read)))
        self.assertEqual(len(stream.peek(10)), 10)
        self.assertTrue(stream.has_more_than(10))
        self.assertEqual(len(read), 11)
        stream.consume(4)
        self.assertEqual(stream.peek(1)[0].values["a"], "row 4")
        self.assertEqual(len(read), 11)

    def test_end_of_rows(self):
        stream = RowStream(table([TableRow(values={"a": "x"})]))
        self.assertEqual(len(stream.peek(5)), 1)
        self.assertFalse(stream.has_more_than(1))


class TableFragmentTests(unittest.TestCase):

    def setUp(self):
        self.table = table([], header="Caption", footer=TableRow(values={"a": "Total"}, kind="total"), table_style=TableStyle(repeat_header=False))

    def test_first_fragment_keeps_caption_and_header(self):
        fragment = TableFragment.of(self.table, [], continued=False, last=False)
        self.assertEqual(fragment.header, "Caption")
        self.assertIsNone(fragment.footer)
        self.assertTrue(fragment.table_style.show_header)

    def test_continued_fragment(self):
        fragment = TableFragment.of(self.table, [], continued=True, last=True, widths=[100.5, 50.25])
        self.assertIsNone(fragment.header)
        self.assertEqual(fragment.footer.values["a"], "Total")
        self.assertFalse(fragment.table_style.show_header)
        self.assertEqual([column.width for column in fragment.columns], ["100.5px", "50.25px"])
        self.assertEqual(self.table.columns[0].width, None)


class ChunkPlannerTests(unittest.TestCase):

    def test_stops_inside_a_table_and_resumes(self):
        read = []
        running = Header(repeat=True, children=[Text(value="Running")])
        document = report(running, Text(value="Intro"), table(counted_rows(25, read)), Text(value="After"))
        flow = ReportFlow(document)
        chunk = ChunkPlanner.plan(flow, 10)
        self.assertFalse(chunk.final)
        page = chunk.report.children[0]
        fragment = page.children[-1]
        self.assertIsInstance(fragment, TableFragment)
        self.assertEqual(len(list(fragment.rows)), 10)
        self.assertEqual(len(read), 11)

        chunk.stream.consume(8)
        chunk.stream.started = True
        flow.advance(chunk.position, chunk.running)
        chunk = ChunkPlanner.plan(flow, 100)
        self.assertTrue(chunk.final)
        children = chunk.report.children[0].children
        self.assertIs(children[0], running)
        self.assertTrue(children[1].continued)
        self.assertEqual([row.values["a"] for row in children[1].rows][:2], ["row 8", "row 9"])
        self.assertEqual(children[2].value, "After")
        self.assertIsInstance(children[3], PageNumber)

    def test_small_report_is_one_final_chunk(self):
        chunk = ChunkPlanner.plan(ReportFlow(report(table([TableRow(values={"a": "x"})]))), 10)
        self.assertTrue(chunk.final)


class PageNumberingTests(unittest.TestCase):

    def test_numbering_can_be_left_out_of_the_margins(self):
        document = report(Text(value="x"))
        self.assertIn("counter(page)", HtmlPageResolver.resolve(document))
        self.assertNotIn("counter(page)", HtmlPageResolver.resolve(document, numbering=False))


@unittest.skipUnless(weasyprint_available(), "WeasyPrint or its system libraries are not installed")
class ChunkedPdfExportTests(unittest.TestCase):
    """
    Chunked layout must produce the same pages as a single pass.
    """

    def build(self, rows=None):
        return report(
            Header(repeat=True, children=[Text(value="Running header")]),
            Footer(repeat=True, children=[Text(value="Running footer")]),
            Text(value="Intro"),
            table(rows if rows is not None else [TableRow(values={"a": f"row {index}", "b": "قيمة"}) for index in range(160)], header="Movements"),
            Text(value="Closing note"),
        )

    @staticmethod
    def texts(pdf):
        import pypdf

        return [page.extract_text() for page in pypdf.PdfReader(io.BytesIO(pdf)).pages]

    def test_chunks_match_single_pass(self):
        single = self.texts(PdfExporter.export(self.build(), options=PdfOptions(chunk_rows=None)))
        chunked = self.texts(PdfExporter.export(self.build(), options=PdfOptions(chunk_rows=40)))
        self.assertGreater(len(single), 3)
        self.assertEqual(single, chunked)
        self.assertIn(f"Page {len(chunked)} of {len(chunked)}", chunked[-1])

    def test_lazy_rows_are_read_once(self):
        read = []
        pdf = PdfExporter.export(self.build(counted_rows(160, read)), options=PdfOptions(chunk_rows=40))
        self.assertEqual(read, list(range(160)))
        self.assertIn("row 159", "".join(self.texts(pdf)))

    def test_parallel_workers_keep_every_row_once(self):
        read = []
        texts = self.texts(PdfExporter.export(self.build(counted_rows(160, read)), options=PdfOptions(chunk_rows=40, workers=2)))
        text = " ".join(texts)
        self.assertEqual(read, list(range(160)))
        for index in (0, 39, 40, 159):
            self.assertEqual(text.count(f"row {index}"), 1, index)  # No row is lost or laid out twice.
        self.assertIn(f"Page {len(texts)} of {len(texts)}", texts[-1])
        self.assertIn("Closing note", texts[-1])

    def test_export_to_path_and_stream(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "report.pdf"
            PdfExporter.export_to(self.build(), path, options=PdfOptions(chunk_rows=40))
            self.assertTrue(path.read_bytes().startswith(b"%PDF"))
        stream = io.BytesIO()
        PdfExporter.export_to(self.build(), stream)
        self.assertTrue(stream.getvalue().startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
