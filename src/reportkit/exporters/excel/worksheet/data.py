from openpyxl.cell import WriteOnlyCell
from openpyxl.utils import get_column_letter

from .cells import check_limits, write_value


class DataSheet:
    """
    Append-only worksheet for the data mode; works with streaming (write-only) and standard workbooks.
    """

    def __init__(self, worksheet, direction):
        """
        Wrap a worksheet that only receives appended rows.
        """
        self.worksheet, self.direction, self.rows, self.columns = worksheet, direction, 0, 0

    def append(self, cells):
        """
        Append one row of (value, style, number_format) triples.
        """
        self.rows, self.columns = self.rows + 1, max(self.columns, len(cells))
        check_limits(self.rows, self.columns)
        self.worksheet.append([self.prepare_cell(value, style, number_format) for value, style, number_format in cells])

    def prepare_cell(self, value, style, number_format):
        """
        Build a write-only cell carrying its own format.
        """
        cell = WriteOnlyCell(self.worksheet)
        write_value(cell, value, style, self.direction, number_format)
        return cell

    def set_column_width(self, column, characters):
        """
        Set a column width; streaming sheets accept this only before rows are written.
        """
        self.worksheet.column_dimensions[get_column_letter(column)].width = characters

    def freeze_header(self):
        """
        Keep the header row visible while scrolling.
        """
        self.worksheet.freeze_panes = "A2"

    def add_filter(self):
        """
        Add an AutoFilter over the written header and rows.
        """
        if self.rows > 1:
            self.worksheet.auto_filter.ref = f"A1:{get_column_letter(self.columns)}{self.rows}"
