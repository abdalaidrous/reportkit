from ..base import BaseHtmlRenderer


class InfoGridRenderer(BaseHtmlRenderer):
    """Render information fields in a responsive grid."""

    template_name = "components/information/info_grid.html"

    def render(self, component, context, engine):
        """Render the information grid."""
        style = engine.styles.resolve(context.resolve_style(component))
        children = self.render_children(component, context, engine)
        return engine.templates.render(self.template_name, component=component, style=style, children=children)
