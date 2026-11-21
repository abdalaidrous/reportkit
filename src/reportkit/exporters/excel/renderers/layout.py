from ....components.information import KeyValue
from ....components.typography import Heading, RichText, Text
from ....styles.style import Style
from ..styles import token
from ..values import component_text
from .base import track_shares

INLINE = (Text, Heading, RichText, KeyValue)


class StackRenderer:
    """
    Render a container's children one below the other.
    """

    def render(self, component, context, engine, region):
        """
        Render each child under the previous one and return the rows used.
        """
        height = 0
        for child in component.children:
            height += engine.render(child, context, region.below(height))
        return height


class ColumnsRenderer:
    """
    Render children side by side in bands of slots, like the HTML grid and flex rows.
    """

    def render(self, component, context, engine, region):
        """
        Render the children band by band and return the rows used.
        """
        shares, height = self.get_shares(component, engine), 0
        for start in range(0, len(component.children), len(shares)):
            slots = region.below(height).split(shares)
            height += max(engine.render(child, context, slot) for child, slot in zip(component.children[start:start + len(shares)], slots))
        return height

    def get_shares(self, component, engine):
        """
        Give every child of a row an equal share.
        """
        return [1] * max(1, len(component.children))


class GridRenderer(ColumnsRenderer):
    """
    Render a Grid with its column tracks (fr, auto, %, px).
    """

    def get_shares(self, component, engine):
        """
        Convert the grid tracks into width shares.
        """
        tracks = ["1fr"] * component.columns if isinstance(component.columns, int) else component.columns.split()
        return track_shares(tracks, engine.sheet.content_pixels)


class InfoGridRenderer(ColumnsRenderer):
    """
    Render an InfoGrid with its configured number of equal columns.
    """

    def get_shares(self, component, engine):
        """
        Give every column an equal share.
        """
        return [1] * component.columns


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


class PageBreakRenderer:
    """
    Render a page break as an Excel row break.
    """

    def render(self, component, context, engine, region):
        """
        Break the printed page before the region row.
        """
        engine.sheet.add_page_break(region.row - 1)
        return 0


class PageNumberRenderer:
    """
    Render page numbering in the printed footer.
    """

    def render(self, component, context, engine, region):
        """
        Put the page number format in the footer; it takes no rows.
        """
        engine.sheet.set_footer(component.format)
        return 0


class StackDataRenderer:
    """
    Visit a container's children in the data mode.
    """

    def render(self, component, context, engine):
        """
        Render every child in order.
        """
        for child in component.children:
            engine.render(child, context)


class ColumnsDataRenderer:
    """
    Write side-by-side texts as one row in the data mode; other children are rendered one by one.
    """

    def render(self, component, context, engine):
        """
        Append inline children as the columns of one row, or render each child in order.
        """
        if component.children and all(isinstance(child, INLINE) for child in component.children):
            engine.information_sheet().append([(engine.value(component_text(child)), Style(), None) for child in component.children])
            return
        for child in component.children:
            engine.render(child, context)


class SkipDataRenderer:
    """
    Declare decorative components (spacing, rules, images, page settings) that carry no data in the data mode.
    """

    def render(self, component, context, engine):
        """
        Write nothing for a decorative component.
        """
