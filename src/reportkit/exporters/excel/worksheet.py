from openpyxl.cell import WriteOnlyCell
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.pagebreak import Break

from ...styles.style import Style
from .exceptions import ExcelExportError
from .styles import get_format
from .values import is_formula_like

MAX_ROWS = 1_048_576
MAX_COLUMNS = 16_384
PAPER_SIZES = {"A3": 8, "A4": 9, "A5": 11, "Letter": 1, "Legal": 5}


def write_value(cell, value, style, direction, number_format=None):
    """
    Write a value with its format; text is always stored as text so it can never run as a formula.
    """
    cell.value = value
    if isinstance(value, str):
        cell.data_type = "s"
        cell.quotePrefix = is_formula_like(value)
    get_format(style, direction).apply(cell)
    if number_format:
        cell.number_format = number_format


def check_limits(row, column):
    """
    Refuse positions beyond the Excel grid instead of writing a truncated sheet.
    """
    if row > MAX_ROWS or column > MAX_COLUMNS:
        raise ExcelExportError(f"Excel worksheets are limited to {MAX_ROWS:,} rows and {MAX_COLUMNS:,} columns; the report needs row {row:,}, column {column:,}.")


class FormattedSheet:
    """
    Random-access worksheet for the formatted mode: cells, merges, sizes, images and print settings.
    """

    def __init__(self, worksheet, direction):
        """
        Wrap a standard worksheet.
        """
        self.worksheet, self.direction, self.last_row, self.last_column = worksheet, direction, 0, 1

    def write(self, row, column, value, style=Style(), number_format=None):
        """
        Write one cell.
        """
        check_limits(row, column)
        write_value(self.worksheet.cell(row=row, column=column), value, style, self.direction, number_format)
        self.last_row, self.last_column = max(self.last_row, row), max(self.last_column, column)

    def merge(self, row, column, width=1, height=1):
        """
        Merge a block of cells when it spans more than one cell.
        """
        if width > 1 or height > 1:
            check_limits(row + height - 1, column + width - 1)
            self.worksheet.merge_cells(start_row=row, start_column=column, end_row=row + height - 1, end_column=column + width - 1)
            self.last_row, self.last_column = max(self.last_row, row + height - 1), max(self.last_column, column + width - 1)

    def set_row_height(self, row, points):
        """
        Set a row height in points, keeping the tallest request.
        """
        dimension = self.worksheet.row_dimensions[row]
        dimension.height = max(dimension.height or 0, points)

    def set_column_width(self, column, characters):
        """
        Set a column width in characters, keeping the widest request.
        """
        dimension = self.worksheet.column_dimensions[get_column_letter(column)]
        dimension.width = max(dimension.width or 0, characters)

    def add_image(self, data, row, column, width=None, height=None):
        """
        Anchor an image at a cell, scaled to the requested size in pixels.
        """
        image = ExcelImage(data)
        if width and height:
            image.width, image.height = width, height
        elif width:
            image.width, image.height = width, round(image.height * width / image.width)
        self.worksheet.add_image(image, f"{get_column_letter(column)}{row}")
        return image.height

    def add_page_break(self, row):
        """
        Start a new printed page after the given row.
        """
        self.worksheet.row_breaks.append(Break(id=row))

    def repeat_rows(self, row):
        """
        Repeat a table header row on every printed page; Excel allows one repeated range per sheet.
        """
        if not self.worksheet.print_title_rows:
            self.worksheet.print_title_rows = f"{row}:{row}"

    def set_footer(self, page_format):
        """
        Print page numbers in the footer, turning {page} and {pages} into Excel codes.
        """
        self.worksheet.oddFooter.center.text = page_format.replace("{page}", "&P").replace("{pages}", "&N")

    def set_page(self, page):
        """
        Apply the Page component print settings.
        """
        setup, margins = self.worksheet.page_setup, self.worksheet.page_margins
        setup.orientation, setup.paperSize = page.orientation, PAPER_SIZES.get(page.size, 9)
        margins.top, margins.right, margins.bottom, margins.left = (millimetres_to_inches(value) for value in (page.margin_top, page.margin_right, page.margin_bottom, page.margin_left))
        self.worksheet.sheet_properties.pageSetUpPr.fitToPage, setup.fitToWidth, setup.fitToHeight = True, 1, 0

    def finish(self):
        """
        Limit printing to the written area.
        """
        if self.last_row:
            self.worksheet.print_area = f"A1:{get_column_letter(self.last_column)}{self.last_row}"


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


def millimetres_to_inches(value):
    """
    Convert a CSS length such as "12mm" to inches for Excel margins.
    """
    divisor = {"mm": 25.4, "cm": 2.54, "in": 1, "pt": 72}.get(str(value)[-2:])
    if divisor is None:
        raise ExcelExportError(f"Page margin {value!r} must use mm, cm, in or pt.")
    return round(float(value[:-2]) / divisor, 3)
