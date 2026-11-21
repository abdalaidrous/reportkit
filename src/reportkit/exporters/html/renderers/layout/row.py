from ..base import BaseHtmlRenderer


class RowRenderer(BaseHtmlRenderer):
    """Render styled horizontal layouts."""

    template_name = "components/layout/row.html"

    @staticmethod
    def resolve_layout(component):
        """Resolve row layout properties."""
        styles = []
        if component.justify:
            styles.append(f"justify-content: {component.justify}")
        if component.align:
            styles.append(f"align-items: {component.align}")
        if component.gap:
            styles.append(f"gap: {component.gap}")
        if component.wrap:
            styles.append("flex-wrap: wrap")
        return "; ".join(styles)

    def render(self, component, context, engine):
        """Render a row with its children and styles."""
        children = self.render_children(component, context, engine)
        style = engine.styles.resolve(context.resolve_style(component))
        layout = self.resolve_layout(component)
        style = "; ".join(part for part in (style, layout) if part)
        return engine.templates.render(self.template_name, children=children, style=style)
