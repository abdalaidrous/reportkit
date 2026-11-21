from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Emu

from .....rendering.tracks import track_shares
from .....styles.borders import edge_borders
from ...styles.xml import SIDES, clear_table_borders, set_bidi_table, set_borders, set_cell_width, set_fixed_layout, set_shading

EMU_PER_PIXEL = 9525


class ColumnsRenderer:
    """
    Render children side by side as a borderless table, one row per band, like the HTML grid and flex rows.
    """

    def render(self, component, context, engine, area):
        """
        Lay the children out band by band in table cells.
        """
        style, shares = context.resolve_style(component), self.get_shares(component, area)
        table = layout_table(engine, area, shares, style)
        for start in range(0, len(component.children), len(shares)):
            for child, cell, share in zip(component.children[start:start + len(shares)], table.add_row().cells, shares):
                engine.render(child, context, layout_cell(area, cell, share / sum(shares), style.background_color))

    def get_shares(self, component, area):
        """
        Give every child of a row an equal share.
        """
        return [1] * max(1, len(component.children))


class GridRenderer(ColumnsRenderer):
    """
    Render a Grid with its column tracks (fr, auto, %, px).
    """

    def get_shares(self, component, area):
        """
        Convert the grid tracks into width shares.
        """
        tracks = ["1fr"] * component.columns if isinstance(component.columns, int) else component.columns.split()
        return track_shares(tracks, area.width / EMU_PER_PIXEL)


class InfoGridRenderer(ColumnsRenderer):
    """
    Render an InfoGrid with its configured number of equal columns.
    """

    def get_shares(self, component, area):
        """
        Give every column an equal share.
        """
        return [1] * component.columns


def layout_table(engine, area, shares, style):
    """
    Create a fixed-width layout table without rows: borderless, right to left when needed, outlined like the component.
    """
    table = area.table(0, len(shares))
    set_fixed_layout(table)
    clear_table_borders(table)
    if engine.direction == "rtl":
        set_bidi_table(table)
    set_borders(table._tbl.tblPr, "w:tblBorders", dict(zip(SIDES, edge_borders(style))))
    for column, share in zip(table.columns, shares):
        column.width = Emu(int(area.width * share / sum(shares)))
    return table


def layout_cell(area, cell, share, background):
    """
    Size a layout cell, give it the component background and return its area.
    """
    width = Emu(int(area.width * share))
    set_cell_width(cell, width)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    if background:
        set_shading(cell._tc.get_or_add_tcPr(), background)
    return area.cell(cell, width)
