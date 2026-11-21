from .....styles.style import Style
from .....styles.tokens import token
from ...styles.text import format_paragraph
from ...styles.xml import child, set_attributes, set_borders


class SpacerRenderer:
    """
    Render vertical spacing using an empty paragraph.
    """

    def render(self, component, context, engine, area):
        """
        Render a paragraph with the configured spacer height.
        """
        if not component.height:
            return

        paragraph = area.paragraph()
        format_paragraph(paragraph, Style(), engine.direction)
        self.apply_height(paragraph, component.height)

    @staticmethod
    def apply_height(paragraph, height):
        """
        Apply the spacer height as an exact line height.
        """
        spacing = child(paragraph._p.get_or_add_pPr(), "w:spacing")
        set_attributes(spacing, line=round(height * 0.75 * 20), lineRule="exact")


class DividerRenderer:
    """
    Render a horizontal divider using a paragraph border.
    """

    def render(self, component, context, engine, area):
        """
        Render a paragraph with the configured bottom border.
        """
        style = self.get_style(component, context)
        paragraph = area.paragraph()

        format_paragraph(paragraph, style, engine.direction)
        self.apply_border(paragraph, style)

    @staticmethod
    def get_style(component, context):
        """
        Resolve the divider style with its default border.
        """
        border = f"1px solid {token('--rk-color-border')}"
        return Style(border_bottom=border).merge(context.resolve_style(component))

    @staticmethod
    def apply_border(paragraph, style):
        """
        Apply the divider bottom border.
        """
        set_borders(paragraph._p.get_or_add_pPr(), "w:pBdr", {"bottom": style.border_bottom})