from ..base import BaseHtmlRenderer


class SectionRenderer(BaseHtmlRenderer):
    """Render styled report sections."""

    template_name = "components/layout/section.html"

    def render(self, component, context, engine):
        """Render a section with its children and styles."""
        children = self.render_children(component, context, engine)
        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(self.template_name, children=children, style=style)
