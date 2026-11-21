from ..base import BaseHtmlRenderer


class DividerRenderer(BaseHtmlRenderer):
    """Render visual separators between report sections."""

    template_name = "components/layout/divider.html"

    def render(self, component, context, engine):
        """Render a divider with its resolved styles."""
        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(self.template_name, style=style)
