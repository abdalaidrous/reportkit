from ..base import BaseHtmlRenderer


class HeadingRenderer(BaseHtmlRenderer):
    """Render heading components using HTML templates."""

    template_name = "components/typography/heading.html"

    def render(self, component, context, engine):
        """Render a heading with its resolved visual style."""
        if not 1 <= component.level <= 6:
            raise ValueError("Heading level must be between 1 and 6.")
        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(self.template_name, component=component, style=style)
