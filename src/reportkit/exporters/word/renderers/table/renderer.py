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
    Render Word tables with captions, headers, rows, footers, and merged cells.
    """

    def render(self, component, context, engine, area):
        """
        Render table rows incrementally while managing pending cell merges.
        """
        styles = table_styles(context.resolve_style(component))
        widths = get_widths(component, area)
        occupied = set()
        pending = []

        self.render_caption(component, context, engine, area)

        table = self.create_table(component, engine, area, widths, styles)
        rows = TableRows(table, engine.spool)

        self.render_header(component, rows, engine, widths, styles)
        rows.hold()
        self.render_rows(component, rows, engine, widths, styles, occupied, pending)
        self.render_footer(component, rows, engine, widths, styles, occupied, pending)
        merge_pending(rows, pending, rows.count - 1, force=True)

    def render_caption(self, component, context, engine, area):
        """
        Render the optional table caption.
        """
        if not component.header:
            return

        style = Style(font_weight=700, font_size=token("--rk-font-lg")).merge(context.resolve_style(component))
        write_paragraph(area.paragraph(), component.header, style, engine.direction)

    def create_table(self, component, engine, area, widths, styles):
        """
        Create a fixed-width Word table with the configured borders and direction.
        """
        table = area.table(0, len(widths))

        set_fixed_layout(table)
        set_cell_margins(table, CELL_PADDING)
        clear_table_borders(table)

        if engine.direction == "rtl":
            set_bidi_table(table)

        self.apply_table_borders(component, table, styles)
        self.apply_column_widths(table, widths)

        return table

    @staticmethod
    def apply_table_borders(component, table, styles):
        """
        Apply the table frame when the ruled style is disabled.
        """
        if component.table_style.ruled:
            return

        borders = {side: styles["frame"].border_left for side in SIDES}
        set_borders(table._tbl.tblPr, "w:tblBorders", borders)

    @staticmethod
    def apply_column_widths(table, widths):
        """
        Apply the configured column widths.
        """
        for column, width in zip(table.columns, widths):
            column.width = width

    def render_header(self, component, rows, engine, widths, styles):
        """
        Render column headers with optional repetition on subsequent pages.
        """
        if not component.table_style.show_header:
            return

        row, _ = rows.add()
        style = self.get_header_style(component, styles)

        set_row_flags(row, repeat_header=component.table_style.repeat_header, cant_split=True)
        size_row(row, widths)

        for cell, column in zip(row.cells, component.columns):
            self.render_header_cell(cell, column, style, engine.direction)

    @staticmethod
    def get_header_style(component, styles):
        """
        Resolve the table header style.
        """
        return styles["header"].merge(styles["ruled"]) if component.table_style.ruled else styles["header"]

    @staticmethod
    def render_header_cell(cell, column, style, direction):
        """
        Render a column header with its alignment.
        """
        cell_style = style.merge(Style(text_align=column.header_align or column.align))
        fill_cell(cell, header_text(column, "\n"), cell_style, direction)

    def render_rows(self, component, rows, engine, widths, styles, occupied, pending):
        """
        Render table rows and flush completed rows.
        """
        for index, table_row in enumerate(component.rows):
            TableValidator.validate_row(table_row)
            self.render_row(component, rows, table_row, index, engine, widths, styles, occupied, pending)
            self.flush_rows(rows, pending)

    def render_footer(self, component, rows, engine, widths, styles, occupied, pending):
        """
        Render the optional table footer.
        """
        if not component.footer:
            return

        self.render_row(component, rows, component.footer, 0, engine, widths, styles, occupied, pending)

    def render_row(self, component, rows, table_row, index, engine, widths, styles, occupied, pending):
        """
        Render a table row and resolve completed cell spans.
        """
        row, number = rows.add()
        row_style = get_row_style(component, table_row, index, styles)

        set_row_flags(row, cant_split=component.table_style.avoid_row_break)
        size_row(row, widths)

        self.render_cells(component, table_row, row, number, row_style, engine.direction, widths, occupied, pending)
        merge_pending(rows, pending, number)

    def render_cells(self, component, table_row, row, number, style, direction, widths, occupied, pending):
        """
        Render row cells and register their spans.
        """
        entries = get_entries(component, table_row)
        cells = row.cells

        for column, entry, colspan, rowspan in place_cells(entries, 0, number, occupied):
            self.validate_cell(column, colspan, len(widths))
            self.render_cell(cells[column], entry, style, direction)
            pending.append((number, column, colspan, rowspan))

    @staticmethod
    def validate_cell(column, colspan, column_count):
        """
        Validate the cell position against the table columns.
        """
        if column + colspan > column_count:
            raise WordExportError(f"A table row has more cells than the table's {column_count} columns.")

    @staticmethod
    def render_cell(cell, entry, style, direction):
        """
        Render a cell with its resolved style.
        """
        text, cell_style = prepare_entry(entry)
        fill_cell(cell, text, style.merge(cell_style), direction)

    @staticmethod
    def flush_rows(rows, pending):
        """
        Flush rows that are no longer required for pending merges.
        """
        position = min((item[0] for item in pending), default=rows.count)
        rows.flush(position)


def merge_pending(rows, pending, current, force=False):
    """
    Merge completed cell spans or finalize remaining spans.
    """
    completed = [item for item in pending if force or item[0] + item[3] - 1 <= current]

    for item in completed:
        merge_cells(rows, item, current)
        pending.remove(item)


def merge_cells(rows, item, current):
    """
    Merge the cells covered by a column or row span.
    """
    start, column, colspan, rowspan = item

    if colspan == 1 and rowspan == 1:
        return

    end = min(start + rowspan - 1, current)
    rows.cell(start, column).merge(rows.cell(end, column + colspan - 1))