from .base import BaseHtmlRenderer


class SectionRenderer(BaseHtmlRenderer):
    """
    Render section containers.
    """

    template_name = "components/section.html"

    def render(self, component, context, engine) -> str:
        """
        Render a section and its children.
        """
        children = self.render_children(component, context, engine)
        return engine.templates.render(self.template_name, children=children)


class RowRenderer(BaseHtmlRenderer):
    """
    Render horizontal component layouts.
    """

    template_name = "components/row.html"

    def render(self, component, context, engine) -> str:
        """
        Render a row and its children.
        """
        children = self.render_children(component, context, engine)
        return engine.templates.render(self.template_name, children=children)


class ColumnRenderer(BaseHtmlRenderer):
    """
    Render vertical component layouts.
    """

    template_name = "components/column.html"

    def render(self, component, context, engine) -> str:
        """
        Render a column and its children.
        """
        children = self.render_children(component, context, engine)
        return engine.templates.render(self.template_name, children=children)
