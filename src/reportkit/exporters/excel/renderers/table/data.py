from .....styles.style import Style
from .....validators.table.table import TableValidator
from ...styles import table_styles
from .cells import get_entries, header_text, prepare_entry
from .placement import place_cells
from .widths import width_characters


class TableDataRenderer:
    """
    Render a Table in the data mode: its own sheet with one header row, typed values, frozen header and AutoFilter.
    """

    def render(self, component, context, engine):
        """
        Stream the rows to a new sheet without loading them in memory.
        """
        sheet, styles, occupied = engine.table_sheet(component), table_styles(), set()
        for index, column in enumerate(component.columns, start=1):
            sheet.set_column_width(index, width_characters(column))
        sheet.freeze_header()
        sheet.append([(header_text(column, " / "), styles["header"], None) for column in component.columns])
        for row_number, table_row in enumerate(component.rows, start=2):
            TableValidator.validate_row(table_row)
            sheet.append(self.prepare_row(component, table_row, row_number, engine, occupied))
        sheet.add_filter()
        if component.footer:
            sheet.append(self.prepare_row(component, component.footer, sheet.rows + 1, engine, occupied))

    @staticmethod
    def prepare_row(component, table_row, row_number, engine, occupied):
        """
        Lay the row out on columns with each cell's style and number format; spanned positions stay empty because data
        sheets do not merge cells.
        """
        weight = Style(font_weight=700) if table_row.kind != "data" else Style()
        placed = {column: prepare_entry(entry, engine) for column, entry, colspan, rowspan in place_cells(get_entries(component, table_row), 1, row_number, occupied)}
        return [(placed[column][0], weight.merge(placed[column][1]), placed[column][2]) if column in placed else (None, Style(), None) for column in range(1, max(placed, default=0) + 1)]
