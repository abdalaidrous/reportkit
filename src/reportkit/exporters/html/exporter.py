from ...components.document import Report
from ...rendering.context import RenderingContext
from ..base import BaseExporter
from .engine import HtmlRenderingEngine
from .page import HtmlPageResolver


class HtmlExporter(BaseExporter):
    """
    Export report documents into complete HTML files.
    """

    def __init__(self, engine=None):
        """
        Initialize the HTML exporter.
        """
        self.engine = engine if engine is not None else HtmlRenderingEngine()

    def export(self, document, context=None) -> bytes:
        """
        Export a report into a UTF-8 HTML document.
        """
        if not isinstance(document, Report):
            raise TypeError("HTML export requires a Report component.")

        context = context if context is not None else RenderingContext()
        content = self.engine.render(document, context)
        page_css = HtmlPageResolver.resolve(document)
        styles = self.engine.templates.load_styles() + "\n" + page_css
        html = self.engine.templates.render(
            "document.html",
            title=document.title,
            language=context.language,
            direction=context.direction,
            content=content,
            styles=styles,
        )
        return html.encode("utf-8")
