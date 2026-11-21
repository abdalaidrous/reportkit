import gc
from collections import deque
from concurrent.futures import ProcessPoolExecutor

from ..conversion import PdfConversionService
from ..resources import PdfResourcePolicy
from .flow import ReportFlow
from .html import ChunkHtmlExporter
from .layout import ChunkLayout
from .planner import ChunkPlanner


def layout_chunk(html, base_url):
    """
    Lay one chunk out in a worker process and return its PDF.
    """
    return PdfConversionService.convert(html, base_url)


class ParallelPdfRenderer:
    """
    Lay a report out in chunks on several processes and yield the chunk PDFs in order.

    The first chunk is laid out here to measure the column widths the others keep. Every chunk keeps its own last
    page, so a page at a chunk boundary may be partly filled; the HTML is built here and only strings cross processes.
    """

    def __init__(self, document, context, base_url, chunk_rows, workers):
        """
        Prepare the parallel layout; numbered tells, after the first chunk, whether the chunks number their own pages.
        """
        self.document = document
        self.context = context
        self.base_url = base_url
        self.chunk_rows = chunk_rows
        self.workers = workers
        self.numbered = None

    def chunks(self):
        """
        Yield chunk PDFs in order, keeping at most two chunks per worker in flight so memory stays bounded.
        """
        flow = ReportFlow(self.document)
        first = ChunkPlanner.plan(flow, self.chunk_rows)
        self.numbered = first.final
        yield self.render_first(flow, first)

        if not first.final:
            yield from self.render_remaining(flow)

    def render_first(self, flow, chunk):
        """
        Lay the first chunk out in this process and keep the column widths of the table it stops inside.
        """
        html = self.export_html(chunk)

        with PdfConversionService.guard() as weasyprint:
            document = PdfConversionService.layout(weasyprint, html, PdfResourcePolicy(self.base_url))
            widths = None if chunk.final else self.column_widths(document)
            pdf = document.write_pdf()

        if not chunk.final:
            self.advance(flow, chunk, widths)

        document = None
        gc.collect()
        return pdf

    def render_remaining(self, flow):
        """
        Submit the remaining chunks to the worker processes and yield their PDFs in report order.
        """
        pool = ProcessPoolExecutor(max_workers=self.workers)
        pending = deque()

        try:
            for html in self.remaining_html(flow):
                pending.append(pool.submit(layout_chunk, html, self.base_url))

                if len(pending) >= self.workers * 2:
                    yield pending.popleft().result()

            while pending:
                yield pending.popleft().result()
        finally:
            pool.shutdown(cancel_futures=True)

    def remaining_html(self, flow):
        """
        Plan the remaining chunks one after another, consuming every row a chunk lays out.
        """
        while True:
            chunk = ChunkPlanner.plan(flow, self.chunk_rows)
            yield self.export_html(chunk)

            if chunk.final:
                return

            self.advance(flow, chunk, None)

    def export_html(self, chunk):
        """
        Export the planned chunk as HTML using the current page numbering mode.
        """
        return ChunkHtmlExporter(numbering=self.numbered).export(chunk.report, self.context).decode("utf-8")

    @staticmethod
    def column_widths(document):
        """
        Return the column widths of the table the first chunk stops inside, or None when it cannot be found.
        """
        layout = ChunkLayout(document.pages)
        return layout.column_widths() if layout.table is not None else None

    @staticmethod
    def advance(flow, chunk, widths):
        """
        Consume every row of the chunk's open table and move the flow past it.
        """
        chunk.stream.consume(chunk.rows)
        chunk.stream.started = True
        chunk.stream.widths = chunk.stream.widths or widths
        flow.advance(chunk.position, chunk.running)
