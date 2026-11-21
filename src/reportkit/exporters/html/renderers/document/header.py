from ..base import BaseHtmlRenderer


class HeaderRenderer(BaseHtmlRenderer):
    """
    Render report header components.
    """

    template_name = "components/document/header.html"

    def render(self, component, context, engine):
        """
        Render the header and its children.
        """
        style = engine.styles.resolve(context.resolve_style(component))
        children = self.render_children(component, context, engine)
        css_class = "rk-header rk-running-header" if component.repeat else "rk-header"
        return engine.templates.render(self.template_name, style=style, children=children, css_class=css_class)
