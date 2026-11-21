from .base import BaseHtmlRenderer


class SpacerRenderer(BaseHtmlRenderer):
    """
    Render empty spacing between report components.
    """

    template_name = "components/spacer.html"

    def render(self, component, context, engine) -> str:
        """
        Render a spacer with the requested height.
        """
        if (
            isinstance(component.height, bool)
            or not isinstance(component.height, (int, float))
            or not 0 <= component.height < float("inf")
        ):
            raise ValueError("Spacer height must be a finite non-negative number.")

        style = engine.styles.resolve(context.resolve_style(component))
        return engine.templates.render(
            self.template_name,
            height=component.height,
            style=style,
        )
