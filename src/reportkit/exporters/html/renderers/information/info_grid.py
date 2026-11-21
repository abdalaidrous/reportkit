from ..base import BaseHtmlRenderer


class InfoGridRenderer(BaseHtmlRenderer):
    """
    Render information fields in a responsive grid.
    """

    template_name = "components/information/info_grid.html"

    def render(self, component, context, engine):
        """
        Render the information grid.
        """
        style = context.resolve_style(component)
        css_class = self.get_class(component, style, context)
        children = self.render_children(component, context, engine)
        return engine.templates.render(self.template_name, component=component, style=engine.styles.resolve(style), flow=css_class, children=children)

    @staticmethod
    def get_class(component, style, context):
        """
        Get the information grid CSS classes.
        """
        direction = style.direction or context.direction
        return f"rk-grid--{direction} rk-grid--cols-{component.columns}"