from .....styles.style import Style
from ...styles import token


class SpacerRenderer:
    """
    Render vertical space as one row of the requested height.
    """

    def render(self, component, context, engine, region):
        """
        Reserve one row sized to the spacer height, or nothing for a zero spacer.
        """
        if not component.height:
            return 0
        engine.sheet.set_row_height(region.row, component.height * 0.75)
        return 1


class DividerRenderer:
    """
    Render a horizontal rule as a bottom border across the region.
    """

    def render(self, component, context, engine, region):
        """
        Draw the rule on one row.
        """
        engine.sheet.place(region.row, region.column, region.width, None, Style(border_bottom=f"1px solid {token('--rk-color-border')}").merge(context.resolve_style(component)))
        return 1
