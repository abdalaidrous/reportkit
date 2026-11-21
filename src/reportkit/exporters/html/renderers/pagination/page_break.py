from ..base import BaseHtmlRenderer


class PageBreakRenderer(BaseHtmlRenderer):
    """
    Render a forced page break.
    """

    template_name = "components/pagination/page_break.html"

    def render(self, component, context, engine):
        """
        Render a page break marker.
        """
        return engine.templates.render(self.template_name)
