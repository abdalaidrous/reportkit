from .base import BaseHtmlRenderer


class TextRenderer(BaseHtmlRenderer):
    """
    Render text components using HTML templates.
    """

    template_name = "components/text.html"

    def render(self, component, context, engine) -> str:
        """
        Render a text component using the shared template engine.
        """
        style = context.resolve_style(component)
        return engine.templates.render(self.template_name, component=component, style=style)
