from ..base import BaseHtmlRenderer


class KeyValueRenderer(BaseHtmlRenderer):
    """Render a labeled information field."""

    template_name = "components/information/key_value.html"

    def render(self, component, context, engine):
        """Render the label and its supplied value."""
        style = engine.styles.resolve(context.resolve_style(component))
        label_style = engine.styles.resolve(component.label_style)
        value_style = engine.styles.resolve(component.value_style)
        return engine.templates.render(self.template_name, component=component, style=style, label_style=label_style, value_style=value_style)
