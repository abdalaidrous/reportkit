from ...html.exporter import HtmlExporter
from ...html.page import HtmlPageResolver


class ChunkHtmlExporter(HtmlExporter):
    """
    Export one chunk to HTML; the page number stays out of the margins when the merged PDF is numbered afterwards.
    """

    def __init__(self, numbering):
        """
        Choose whether the chunk numbers its own pages.
        """
        super().__init__()
        self.numbering = numbering

    def page_styles(self, document):
        """
        Return the print CSS of the chunk pages.
        """
        return HtmlPageResolver.resolve(document, numbering=self.numbering)
