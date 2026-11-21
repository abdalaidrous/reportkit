from .base import BaseHtmlRenderer


class SectionRenderer(BaseHtmlRenderer):
    """
    Render styled report sections.
    """

    template_name = "components/section.html"

    def render(self, component, context, engine) -> str:
        """
        Render a section with its children and styles.
        """
        children = self.render_children(component, context, engine)
        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(self.template_name, children=children, style=style)


class RowRenderer(BaseHtmlRenderer):
    """
    Render styled horizontal layouts.
    """

    template_name = "components/row.html"

    def render(self, component, context, engine) -> str:
        """
        Render a row with its children and styles.
        """
        children = self.render_children(component, context, engine)
        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(self.template_name, children=children, style=style)


class ColumnRenderer(BaseHtmlRenderer):
    """
    Render styled vertical layouts.
    """

    template_name = "components/column.html"

    def render(self, component, context, engine) -> str:
        """
        Render a column with its children and styles.
        """
        children = self.render_children(component, context, engine)
        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(self.template_name, children=children, style=style)
