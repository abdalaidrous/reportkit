from ..base import BaseHtmlRenderer


class ImageRenderer(BaseHtmlRenderer):
    """Render images into HTML."""

    template_name = "components/media/image.html"

    def render(self, component, context, engine):
        """Render an image with its presentation properties."""
        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(self.template_name, component=component, style=style)
