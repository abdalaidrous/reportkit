from ..base import BaseHtmlRenderer


class PageRenderer(BaseHtmlRenderer):
    """
    Render a report page.
    """

    template_name = "components/document/page.html"

    def render(self, component, context, engine):
        """
        Render page content and print settings.
        """
        style = engine.styles.resolve(context.resolve_style(component))
        children = self.render_children(component, context, engine)
        return engine.templates.render(self.template_name, component=component, children=children, style=style)
