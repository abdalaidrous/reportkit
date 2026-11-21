from .....rendering.table import get_entries, header_text, place_cells
from .....styles.style import Style
from .....styles.table import get_row_style, table_styles
from .....styles.tokens import token
from .....validators.table.table import TableValidator
from ...exceptions import WordExportError
from ...styles.text import write_paragraph
from ...styles.xml import SIDES, clear_table_borders, set_bidi_table, set_borders, set_cell_margins, set_fixed_layout, set_row_flags
from .cells import fill_cell, prepare_entry, size_row
from .rows import TableRows
from .widths import get_widths

CELL_PADDING = 80


class TableRenderer:
    """
    Render a Table: caption, repeated header row, prepared rows and footer, with spans and the PDF table styles.
    """

    def render(self, component, context, engine, area):
        """
        Write the rows in the order they arrive, adding Word rows one at a time; finished rows leave memory.
        """
        styles, widths, occupied, pending = table_styles(context.resolve_style(component)), get_widths(component, area), set(), []
        self.render_caption(component, context, engine, area)
        rows = TableRows(self.create_table(component, engine, area, widths, styles), engine.spool)
        self.render_header(component, rows, engine, widths, styles)
        rows.hold()
        for index, table_row in enumerate(component.rows):
            TableValidator.validate_row(table_row)
            self.render_row(component, rows, table_row, index, engine, widths, styles, occupied, pending)
            rows.flush(min((item[0] for item in pending), default=rows.count))
        if component.footer:
            self.render_row(component, rows, component.footer, 0, engine, widths, styles, occupied, pending)
        merge_pending(rows, pending, rows.count - 1, force=True)

    def render_caption(self, component, context, engine, area):
        """
        Write the table caption above the table when it has one.
        """
        if component.header:
            write_paragraph(area.paragraph(), component.header, Style(font_weight=700, font_size=token("--rk-font-lg")).merge(context.resolve_style(component)), engine.direction)

    def create_table(self, component, engine, area, widths, styles):
        """
        Create the empty fixed-width table, right to left when needed, with the frame unless it is ruled.
        """
        table = area.table(0, len(widths))
        set_fixed_layout(table)
        set_cell_margins(table, CELL_PADDING)
        clear_table_borders(table)
        if engine.direction == "rtl":
            set_bidi_table(table)
        if not component.table_style.ruled:
            set_borders(table._tbl.tblPr, "w:tblBorders", {side: styles["frame"].border_left for side in SIDES})
        for column, width in zip(table.columns, widths):
            column.width = width
        return table

    def render_header(self, component, rows, engine, widths, styles):
        """
        Write the column titles and subtitles, repeated on every page when requested.
        """
        if not component.table_style.show_header:
            return
        (row, _), style = rows.add(), styles["header"].merge(styles["ruled"]) if component.table_style.ruled else styles["header"]
        set_row_flags(row, repeat_header=component.table_style.repeat_header, cant_split=True)
        size_row(row, widths)
        for cell, column in zip(row.cells, component.columns):
            fill_cell(cell, header_text(column, "\n"), style.merge(Style(text_align=column.header_align or column.align)), engine.direction)

    def render_row(self, component, rows, table_row, index, engine, widths, styles, occupied, pending):
        """
        Write one prepared row, merging cells that span columns now and rows once the later rows exist.
        """
        (row, number), row_style = rows.add(), get_row_style(component, table_row, index, styles)
        set_row_flags(row, cant_split=component.table_style.avoid_row_break)
        size_row(row, widths)
        cells = row.cells
        for column, entry, colspan, rowspan in place_cells(get_entries(component, table_row), 0, number, occupied):
            if column + colspan > len(widths):
                raise WordExportError(f"A table row has more cells than the table's {len(widths)} columns.")
            text, cell_style = prepare_entry(entry)
            fill_cell(cells[column], text, row_style.merge(cell_style), engine.direction)
            pending.append((number, column, colspan, rowspan))
        merge_pending(rows, pending, number)


def merge_pending(rows, pending, current, force=False):
    """
    Merge the spans whose last row now exists (or all remaining ones at the end of the table).
    """
    for item in [item for item in pending if force or item[0] + item[3] - 1 <= current]:
        start, column, colspan, rowspan = item
        if colspan > 1 or rowspan > 1:
            rows.cell(start, column).merge(rows.cell(min(start + rowspan - 1, current), column + colspan - 1))
        pending.remove(item)
