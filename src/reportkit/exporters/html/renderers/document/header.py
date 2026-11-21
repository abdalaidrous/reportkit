from ..base import BaseHtmlRenderer


class HeaderRenderer(BaseHtmlRenderer):
    """Render report header components."""

    template_name = "components/document/header.html"

    def render(self, component, context, engine):
        """Render the header and its children."""
        style = engine.styles.resolve(context.resolve_style(component))
        children = self.render_children(component, context, engine)
        return engine.templates.render(self.template_name, style=style, children=children)
