from ..base import BaseHtmlRenderer


class ColumnRenderer(BaseHtmlRenderer):
    """
    Render styled vertical layouts.
    """

    template_name = "components/layout/column.html"

    @staticmethod
    def resolve_layout(component):
        """
        Resolve column layout properties.
        """
        styles = []
        if component.align not in (None, "start", "center", "end", "stretch"):
            raise ValueError("Invalid column alignment.")
        if component.justify not in (None, "start", "center", "end", "space-between", "space-around", "space-evenly"):
            raise ValueError("Invalid column justification.")
        if component.direction not in (None, "ltr", "rtl"):
            raise ValueError("Invalid column direction.")
        if component.align:
            styles.append(f"align-items: {component.align}")
        if component.justify:
            styles.append(f"justify-content: {component.justify}")
        if component.gap:
            styles.append(f"gap: {component.gap}")
        if component.direction:
            styles.append(f"direction: {component.direction}")
        return "; ".join(styles)

    def render(self, component, context, engine):
        """
        Render a column with its children and styles.
        """
        children = self.render_children(component, context, engine)
        style = engine.styles.resolve(context.resolve_style(component))
        layout = self.resolve_layout(component)
        style = "; ".join(part for part in (style, layout) if part)
        return engine.templates.render(self.template_name, children=children, style=style)
