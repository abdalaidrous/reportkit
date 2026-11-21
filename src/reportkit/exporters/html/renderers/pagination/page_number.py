from ..base import BaseHtmlRenderer


class PageNumberRenderer(BaseHtmlRenderer):
    """
    Render a page numbering placeholder.
    """

    template_name = "components/pagination/page_number.html"

    def render(self, component, context, engine):
        """
        Render the page numbering format.
        """
        return ""
