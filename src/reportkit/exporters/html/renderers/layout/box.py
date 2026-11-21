from ..base import BaseHtmlRenderer


class BoxRenderer(BaseHtmlRenderer):
    """
    Render a styled box and its child components.
    """

    template_name = "components/layout/box.html"

    def render(self, component, context, engine):
        """
        Render a box using its resolved style.
        """
        style = engine.styles.resolve(context.resolve_style(component))
        children = self.render_children(component, context, engine)
        return engine.templates.render(self.template_name, style=style, children=children)
