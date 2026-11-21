from ..base import BaseExporter
from ..html.exporter import HtmlExporter
from .conversion import PdfConversionService


class PdfExporter(BaseExporter):
    """
    Export a report to PDF bytes: HtmlExporter builds the HTML, PdfConversionService converts it.
    """

    @classmethod
    def export(cls, document, context=None, base_url=None) -> bytes:
        """
        Render the report to HTML and convert it; base_url is the only folder local files may come from.
        """
        return PdfConversionService.convert(HtmlExporter().export(document, context).decode("utf-8"), base_url)
