from ....components.typography import Heading
from ....styles.style import Style
from ....styles.tokens import token
from ..values import cell_value, component_text

HEADING_SIZES = {1: "--rk-font-2xl", 2: "--rk-font-xl", 3: "--rk-font-lg"}


class TextRenderer:
    """
    Render Text, Heading and RichText as one merged cell across the region.
    """

    def render(self, component, context, engine, region):
        """
        Write the text and return the single row it uses.
        """
        engine.sheet.place(region.row, region.column, region.width, cell_value(component_text(component)), self.get_style(component, context))
        return 1

    def get_style(self, component, context):
        """
        Use the component style, with the heading defaults for headings.
        """
        style = context.resolve_style(component)
        if isinstance(component, Heading):
            return Style(font_weight=700, font_size=token(HEADING_SIZES.get(component.level, "--rk-font-md"))).merge(style)
        return style


class TextDataRenderer:
    """
    Write text components as one-cell rows on the report information sheet.
    """

    def render(self, component, context, engine):
        """
        Append the text to the information sheet.
        """
        engine.information_sheet().append([(cell_value(component_text(component)), Style(font_weight=700) if isinstance(component, Heading) else Style(), None)])
