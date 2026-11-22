import gc

from ..conversion import PdfConversionService
from ..resources import PdfResourcePolicy
from .flow import ReportFlow
from .html import ChunkHtmlExporter
from .layout import ChunkLayout
from .planner import ChunkPlanner
from .slots import PageCountLedger


class ChunkedPdfRenderer:
    """
    Lay a report out chunk by chunk and yield the PDF of each chunk, so only one chunk is in memory at a time.
    """

    def __init__(self, document, context, base_url, chunk_rows):
        """
        Prepare the chunked layout; numbered tells, after the first chunk, whether the chunks number their own pages,
        and counts collects where the deferred page counts of the yielded chunks wait for the merged page total.
        """
        self.document = document
        self.context = context
        self.policy = PdfResourcePolicy(base_url)
        self.chunk_rows = chunk_rows
        self.numbered = None
        self.counts = PageCountLedger(document)

    def chunks(self):
        """
        Yield chunk PDFs in order; a report that fits one chunk is laid out exactly once and numbers its own pages.
        """
        flow = ReportFlow(self.document)
        limit = self.chunk_rows

        while True:
            chunk = self.plan(flow, limit)
            pdf, consumed, widths, laid_out = self.render(chunk)
            gc.collect()  # WeasyPrint boxes form reference cycles; free each chunk before laying out the next.

            if not self.accepted(flow, chunk, pdf, consumed):
                limit *= 2  # The chunk ended too early to cut at a page break: lay more rows out together.
                continue

            self.counts.keep(laid_out)
            yield pdf

            if chunk.final:
                return

            self.advance(flow, chunk, consumed, widths)
            limit = self.chunk_rows

    def plan(self, flow, limit):
        """
        Plan the next chunk and determine whether its pages should be numbered independently.
        """
        chunk = ChunkPlanner.plan(flow, limit)

        if self.numbered is None:
            self.numbered = chunk.final

        return chunk

    def render(self, chunk):
        """
        Lay the chunk out and return its PDF without the dropped last page, the rows laid out, the column widths and
        (kept pages, page count slots); the PDF is None when the chunk cannot be cut at a page break.
        """
        html = self.export_html(chunk)

        with PdfConversionService.guard() as weasyprint:
            document = PdfConversionService.layout(weasyprint, html, self.policy)
            return self.render_document(document, chunk)

    def export_html(self, chunk):
        """
        Export the planned chunk as HTML using the current page numbering mode.
        """
        return ChunkHtmlExporter(numbering=self.numbered).export(chunk.report, self.context).decode("utf-8")

    def render_document(self, document, chunk):
        """
        Write the complete PDF for the last chunk, or keep only the pages before the continuation boundary.
        """
        if chunk.final:
            return document.write_pdf(), 0, None, self.counts.laid_out(document.pages)

        return self.render_partial(document)

    def render_partial(self, document):
        """
        Keep complete pages before the continuation boundary and return their consumed rows and column widths.
        """
        layout = ChunkLayout(document.pages)

        if not layout.accepted:
            return None, 0, None, (0, [])

        return document.copy(layout.kept).write_pdf(), layout.consumed_rows(), layout.column_widths(), self.counts.laid_out(layout.kept)

    @classmethod
    def accepted(cls, flow, chunk, pdf, consumed):
        """
        Return whether the rendered chunk can be kept and advances the report flow.
        """
        return pdf is not None and cls.advances(flow, chunk, consumed)

    @staticmethod
    def advances(flow, chunk, consumed):
        """
        Return whether keeping the chunk moves the flow forward.
        """
        return chunk.final or chunk.position != flow.position or consumed > 0 or not chunk.stream.started

    @staticmethod
    def advance(flow, chunk, consumed, widths):
        """
        Consume the rendered table rows, preserve column widths and advance the flow to the next chunk.
        """
        chunk.stream.consume(consumed)
        chunk.stream.started = True
        chunk.stream.widths = chunk.stream.widths or widths
        flow.advance(chunk.position, chunk.running)