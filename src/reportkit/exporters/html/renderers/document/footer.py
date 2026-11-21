from ..base import BaseHtmlRenderer


class FooterRenderer(BaseHtmlRenderer):
    """Render report footer components."""

    template_name = "components/document/footer.html"

    def render(self, component, context, engine):
        """Render the footer and its children."""
        style = engine.styles.resolve(context.resolve_style(component))
        children = self.render_children(component, context, engine)
        return engine.templates.render(self.template_name, style=style, children=children)
