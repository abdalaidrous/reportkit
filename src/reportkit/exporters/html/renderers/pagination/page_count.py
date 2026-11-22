from ...direction import text_direction
from ..base import BaseHtmlRenderer


class PageCountRenderer(BaseHtmlRenderer):
    """
    Render the total page count; the number itself comes from the PDF layout (CSS counter(pages)).
    """

    template_name = "components/pagination/page_count.html"

    def render(self, component, context, engine):
        """
        Render the text around the page total; a deferred count is laid out hidden and stamped after the merge.
        """
        style = engine.styles.resolve(context.resolve_style(component))
        before, after = component.parts
        return engine.templates.render(self.template_name, component=component, before=before, after=after, style=style, deferred=engine.defer_page_count, text_dir=text_direction(component.format))
