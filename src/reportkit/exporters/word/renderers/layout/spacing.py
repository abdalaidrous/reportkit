from .....styles.style import Style
from .....styles.tokens import token
from ...styles.text import format_paragraph
from ...styles.xml import child, set_attributes, set_borders


class SpacerRenderer:
    """
    Render vertical space as an empty paragraph of the requested height.
    """

    def render(self, component, context, engine, area):
        """
        Add a paragraph whose line height is the spacer height.
        """
        if component.height:
            paragraph = area.paragraph()
            format_paragraph(paragraph, Style(), engine.direction)
            set_attributes(child(paragraph._p.get_or_add_pPr(), "w:spacing"), line=round(component.height * 0.75 * 20), lineRule="exact")


class DividerRenderer:
    """
    Render a horizontal rule as a paragraph bottom border.
    """

    def render(self, component, context, engine, area):
        """
        Add an empty paragraph with the rule under it.
        """
        paragraph, style = area.paragraph(), Style(border_bottom=f"1px solid {token('--rk-color-border')}").merge(context.resolve_style(component))
        format_paragraph(paragraph, style, engine.direction)
        set_borders(paragraph._p.get_or_add_pPr(), "w:pBdr", {"bottom": style.border_bottom})
