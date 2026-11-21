from ....styles.style import Style
from ....styles.tokens import token
from ..styles.text import add_run, format_paragraph


class KeyValueRenderer:
    """
    Render a label and its value: on one line for horizontal, on two lines for vertical.
    """

    def render(self, component, context, engine, area):
        """
        Write the label run and the value run.
        """
        style, value = context.resolve_style(component), "" if component.value is None else str(component.value)
        label_style, value_style = Style(color=token("--rk-color-muted")).merge(style).merge(component.label_style), Style(font_weight=600).merge(style).merge(component.value_style)
        paragraph = area.paragraph()
        format_paragraph(paragraph, style, engine.direction)
        add_run(paragraph, self.get_label(component) + ("" if component.orientation == "vertical" else "  "), label_style, engine.direction)
        if component.orientation == "vertical":
            paragraph = area.paragraph()
            format_paragraph(paragraph, style, engine.direction)
        add_run(paragraph, value, value_style, engine.direction)

    @staticmethod
    def get_label(component):
        """
        Join the label and its secondary label.
        """
        return f"{component.label} / {component.secondary_label}" if component.secondary_label else component.label
