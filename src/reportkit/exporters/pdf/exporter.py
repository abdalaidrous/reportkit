import os
import warnings
from io import BytesIO

from ...components.document import Report
from ...rendering.context import RenderingContext
from ..base import BaseExporter
from ..html.exporter import HtmlExporter
from .assembly import PageNumberOverlay, PdfMerger
from .chunking import ChunkedPdfRenderer
from .conversion import PdfConversionService
from .dependencies import PYPDF_HELP, load_pypdf
from .options import PdfOptions


class PdfExporter(BaseExporter):
    """
    Export a report to PDF: HtmlExporter builds the HTML and PdfConversionService converts it, in one pass for small
    reports and in chunks merged with pypdf for large ones.
    """

    @classmethod
    def export(cls, document, context=None, base_url=None, options=None) -> bytes:
        """
        Return the PDF bytes; base_url is the only folder local files may come from.
        """
        buffer = BytesIO()
        cls.export_to(document, buffer, context, base_url, options)
        return buffer.getvalue()

    @classmethod
    def export_to(cls, document, target, context=None, base_url=None, options=None):
        """
        Write the PDF to a file path or a binary stream, without keeping a second copy of it in memory.
        """
        cls.validate(document)
        context = context if context is not None else RenderingContext()
        options = options if options is not None else PdfOptions()

        if options.chunk_rows is None or not cls.can_merge():
            return cls.export_single(document, target, context, base_url)

        return cls.export_chunked(document, target, context, base_url, options.chunk_rows)

    @staticmethod
    def validate(document):
        """
        Require a Report component before starting PDF export.
        """
        if not isinstance(document, Report):
            raise TypeError("PDF export requires a Report component.")

    @classmethod
    def export_single(cls, document, target, context, base_url):
        """
        Lay the complete report out in one pass and write its PDF to the target.
        """
        html = HtmlExporter().export(document, context).decode("utf-8")
        return cls.write(target, PdfConversionService.convert(html, base_url))

    @classmethod
    def export_chunked(cls, document, target, context, base_url, chunk_rows):
        """
        Lay the report out in chunks and merge their PDFs unless the whole report fits in the first chunk.
        """
        renderer = ChunkedPdfRenderer(document, context, base_url, chunk_rows)
        chunks = renderer.chunks()
        first = next(chunks)

        if renderer.numbered:
            return cls.write(target, first)  # The whole report fit in one chunk: a single-pass layout.

        merger = cls.merge_chunks(first, chunks)
        cls.apply_numbering(merger, document, context)
        merger.write(target)

    @staticmethod
    def merge_chunks(first, chunks):
        """
        Append the first PDF and all remaining chunk PDFs to a single merger in report order.
        """
        merger = PdfMerger()
        merger.append(first)

        for pdf in chunks:
            merger.append(pdf)

        return merger

    @staticmethod
    def apply_numbering(merger, document, context):
        """
        Stamp the merged pages with their final page numbers when the report defines page numbering.
        """
        overlay = PageNumberOverlay(document, context)

        if overlay.numbering:
            merger.stamp(overlay.pdfs(merger.page_count))

    @staticmethod
    def can_merge():
        """
        Return whether pypdf is installed; without it large reports fall back to a single-pass layout.
        """
        try:
            load_pypdf()
        except ImportError:
            warnings.warn(PYPDF_HELP + "; laying the whole report out in one pass.", RuntimeWarning, stacklevel=3)
            return False

        return True

    @staticmethod
    def write(target, data):
        """
        Write bytes to a file path or a binary stream.
        """
        if isinstance(target, (str, os.PathLike)):
            with open(target, "wb") as file:
                file.write(data)
        else:
            target.write(data)