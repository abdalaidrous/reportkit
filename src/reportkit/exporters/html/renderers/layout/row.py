from ..base import BaseHtmlRenderer


class RowRenderer(BaseHtmlRenderer):
    """Render styled horizontal layouts."""

    template_name = "components/layout/row.html"

    def render(self, component, context, engine):
        """Render a row with its children and styles."""
        children = self.render_children(component, context, engine)
        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(self.template_name, children=children, style=style)
