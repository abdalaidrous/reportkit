from .base import BaseHtmlRenderer


class TextRenderer(BaseHtmlRenderer):
    """
    Render text components using HTML templates.
    """

    template_name = "components/text.html"

    def render(self, component, context, engine) -> str:
        """
        Render text with its resolved visual style.
        """
        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(self.template_name, component=component, style=style)


class HeadingRenderer(BaseHtmlRenderer):
    """
    Render heading components using HTML templates.
    """

    template_name = "components/heading.html"

    def render(self, component, context, engine) -> str:
        """
        Render a heading with its resolved visual style.
        """
        if not 1 <= component.level <= 6:
            raise ValueError("Heading level must be between 1 and 6.")

        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(self.template_name, component=component, style=style)
