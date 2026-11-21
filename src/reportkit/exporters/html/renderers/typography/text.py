from ..base import BaseHtmlRenderer


class TextRenderer(BaseHtmlRenderer):
    """Render text components using HTML templates."""

    template_name = "components/typography/text.html"

    def render(self, component, context, engine):
        """Render text with its resolved visual style."""
        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(self.template_name, component=component, style=style)
