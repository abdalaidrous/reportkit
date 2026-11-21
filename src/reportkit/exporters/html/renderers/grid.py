from .base import BaseHtmlRenderer


class GridRenderer(BaseHtmlRenderer):
    """
    Render report components in a grid layout.
    """

    template_name = "components/grid.html"

    def render(self, component, context, engine) -> str:
        """
        Render grid columns and nested components.
        """
        if not isinstance(component.columns, int) or isinstance(component.columns, bool) or component.columns < 1:
            raise ValueError("Grid columns must be a positive integer.")

        children = self.render_children(component, context, engine)
        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(self.template_name, children=children, columns=component.columns, style=style)