from ....components.information import KeyValue
from ....components.typography import Heading, RichText, Text
from ....styles.style import Style
from ..styles import token
from ..values import component_text

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


class PageRenderer(StackRenderer):
    """
    Render a page and apply its print settings to the worksheet.
    """

    def render(self, component, context, engine, region):
        """
        Apply orientation, paper size and margins, then render the children.
        """
        engine.sheet.set_page(component)
        return super().render(component, context, engine, region)


class ColumnsRenderer:
    """
    Render children side by side in bands of equal slots, like the HTML grid.
    """

    def render(self, component, context, engine, region):
        """
        Render the children band by band and return the rows used.
        """
        tracks, height = self.get_tracks(component), 0
        for start in range(0, len(component.children), tracks):
            height += self.render_band(component.children[start:start + tracks], context, engine, region.below(height), tracks)
        return height

    def render_band(self, children, context, engine, region, tracks):
        """
        Render one band of children and return the height of the tallest one.
        """
        return max(engine.render(child, context, slot) for child, slot in zip(children, region.split(tracks)))

    def get_tracks(self, component):
        """
        Return the number of side-by-side slots.
        """
        return max(1, len(component.children))


class GridRenderer(ColumnsRenderer):
    """
    Render a Grid using its column track count.
    """

    def get_tracks(self, component):
        """
        Count the grid column tracks.
        """
        return component.columns if isinstance(component.columns, int) else len(component.columns.split())


class InfoGridRenderer(ColumnsRenderer):
    """
    Render an InfoGrid using its configured columns.
    """

    def get_tracks(self, component):
        """
        Return the configured column count.
        """
        return component.columns


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
        style = Style(border_bottom=f"1px solid {token('--rk-color-border')}").merge(context.resolve_style(component))
        for column in range(region.column, region.column + region.width):
            engine.sheet.write(region.row, column, None, style)
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
