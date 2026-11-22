from ...html.engine import HtmlRenderingEngine
from ...html.exporter import HtmlExporter
from ...html.page import HtmlPageResolver


class ChunkHtmlExporter(HtmlExporter):
    """
    Export one chunk to HTML; when the merged PDF is numbered afterwards, the page number stays out of the margins and
    every PageCount is laid out hidden, to be stamped once the page total is known.
    """

    def __init__(self, numbering):
        """
        Choose whether the chunk numbers its own pages and counts them.
        """
        super().__init__(HtmlRenderingEngine(defer_page_count=not numbering))
        self.numbering = numbering

    def page_styles(self, document):
        """
        Return the print CSS of the chunk pages.
        """
        return HtmlPageResolver.resolve(document, numbering=self.numbering)
