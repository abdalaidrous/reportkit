from ..base import BaseHtmlRenderer


class ColumnRenderer(BaseHtmlRenderer):
    """Render styled vertical layouts."""

    template_name = "components/layout/column.html"

    def render(self, component, context, engine):
        """Render a column with its children and styles."""
        children = self.render_children(component, context, engine)
        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(self.template_name, children=children, style=style)
