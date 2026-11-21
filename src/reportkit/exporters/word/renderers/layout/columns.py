from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Emu

from .....rendering.tracks import track_shares
from .....styles.borders import edge_borders
from ...styles.xml import SIDES, clear_table_borders, set_bidi_table, set_borders, set_cell_width, set_fixed_layout, set_shading


EMU_PER_PIXEL = 9525


class ColumnsRenderer:
    """
    Render children side by side using a Word layout table.
    """

    def render(self, component, context, engine, area):
        """
        Render children in table rows based on their column shares.
        """
        style = context.resolve_style(component)
        shares = self.get_shares(component, area)
        table = layout_table(engine, area, shares, style)

        for start in range(0, len(component.children), len(shares)):
            children = component.children[start:start + len(shares)]
            self.render_row(children, table, shares, style, context, engine, area)

    @staticmethod
    def render_row(children, table, shares, style, context, engine, area):
        """
        Render a row of children inside layout cells.
        """
        row = table.add_row()
        total = sum(shares)

        for child, cell, share in zip(children, row.cells, shares):
            cell_area = layout_cell(area, cell, share / total, style.background_color)
            engine.render(child, context, cell_area)

    def get_shares(self, component, area):
        """
        Return equal width shares for the component children.
        """
        return [1] * max(1, len(component.children))


class GridRenderer(ColumnsRenderer):
    """
    Render grid children using their configured column tracks.
    """

    def get_shares(self, component, area):
        """
        Resolve grid tracks into proportional width shares.
        """
        tracks = self.get_tracks(component)
        return track_shares(tracks, area.width / EMU_PER_PIXEL)

    @staticmethod
    def get_tracks(component):
        """
        Return the configured grid column tracks.
        """
        return ["1fr"] * component.columns if isinstance(component.columns, int) else component.columns.split()


class InfoGridRenderer(ColumnsRenderer):
    """
    Render information grid children using equal column widths.
    """

    def get_shares(self, component, area):
        """
        Return equal width shares for the configured columns.
        """
        return [1] * component.columns


def layout_table(engine, area, shares, style):
    """
    Create a fixed-width layout table with the configured direction and borders.
    """
    table = area.table(0, len(shares))

    set_fixed_layout(table)
    clear_table_borders(table)
    apply_table_direction(table, engine.direction)
    apply_table_borders(table, style)
    apply_table_widths(table, area.width, shares)

    return table


def apply_table_direction(table, direction):
    """
    Apply right-to-left layout when required.
    """
    if direction == "rtl":
        set_bidi_table(table)


def apply_table_borders(table, style):
    """
    Apply the component borders to the layout table.
    """
    borders = dict(zip(SIDES, edge_borders(style)))
    set_borders(table._tbl.tblPr, "w:tblBorders", borders)


def apply_table_widths(table, width, shares):
    """
    Apply proportional widths to the table columns.
    """
    total = sum(shares)

    for column, share in zip(table.columns, shares):
        column.width = Emu(int(width * share / total))


def layout_cell(area, cell, share, background):
    """
    Configure a layout cell and return its rendering area.
    """
    width = Emu(int(area.width * share))

    set_cell_width(cell, width)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    apply_cell_background(cell, background)

    return area.cell(cell, width)


def apply_cell_background(cell, background):
    """
    Apply the configured background color to a layout cell.
    """
    if background:
        set_shading(cell._tc.get_or_add_tcPr(), background)