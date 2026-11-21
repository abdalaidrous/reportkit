from ....styles.style import Style
from ....styles.tokens import token
from ..styles.text import add_run, format_paragraph


class KeyValueRenderer:
    """
    Render key-value pairs horizontally or vertically.
    """

    def render(self, component, context, engine, area):
        """
        Render the label and value with their configured styles.
        """
        style = context.resolve_style(component)
        label_style = self.get_label_style(component, style)
        value_style = self.get_value_style(component, style)

        paragraph = self.create_paragraph(area, style, engine.direction)
        self.render_label(paragraph, component, label_style, engine.direction)

        if component.orientation == "vertical":
            paragraph = self.create_paragraph(area, style, engine.direction)

        self.render_value(paragraph, component, value_style, engine.direction)

    @staticmethod
    def create_paragraph(area, style, direction):
        """
        Create and format a paragraph.
        """
        paragraph = area.paragraph()
        format_paragraph(paragraph, style, direction)
        return paragraph

    @classmethod
    def render_label(cls, paragraph, component, style, direction):
        """
        Render the label with its optional spacing.
        """
        label = cls.get_label(component)
        spacing = "" if component.orientation == "vertical" else "  "
        add_run(paragraph, label + spacing, style, direction)

    @staticmethod
    def render_value(paragraph, component, style, direction):
        """
        Render the component value.
        """
        value = "" if component.value is None else str(component.value)
        add_run(paragraph, value, style, direction)

    @staticmethod
    def get_label(component):
        """
        Return the label with its optional secondary label.
        """
        return f"{component.label} / {component.secondary_label}" if component.secondary_label else component.label

    @staticmethod
    def get_label_style(component, style):
        """
        Resolve the label style.
        """
        return Style(color=token("--rk-color-muted")).merge(style).merge(component.label_style)

    @staticmethod
    def get_value_style(component, style):
        """
        Resolve the value style.
        """
        return Style(font_weight=600).merge(style).merge(component.value_style)