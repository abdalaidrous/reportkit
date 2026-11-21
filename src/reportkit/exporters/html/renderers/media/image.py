from ..base import BaseHtmlRenderer
from ...assets import AssetResolver


class ImageRenderer(BaseHtmlRenderer):
    """
    Render images into HTML.
    """

    template_name = "components/media/image.html"

    def render(self, component, context, engine):
        """
        Render an image with its presentation properties.
        """
        style = engine.styles.resolve(context.resolve_style(component))
        source = AssetResolver.resolve(component.src)
        return engine.templates.render(self.template_name, component=component, source=source, style=style)
