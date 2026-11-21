import math

from openpyxl.cell import WriteOnlyCell
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.styles import Border
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.pagebreak import Break

from ...styles.style import Style
from .exceptions import ExcelExportError
from .styles import get_fill, get_format, get_side, pixels, token
from .values import is_formula_like

MAX_ROWS = 1_048_576
MAX_COLUMNS = 16_384
GRID_COLUMNS = 40
PAPER_SIZES = {"A3": 8, "A4": 9, "A5": 11, "Letter": 1, "Legal": 5}
PAPER_MILLIMETRES = {"A3": (297, 420), "A4": (210, 297), "A5": (148, 210), "Letter": (216, 279), "Legal": (216, 356)}
PIXELS_PER_MILLIMETRE = 96 / 25.4
CHARACTER_WIDTH = 0.55
LINE_HEIGHT = 1.3
SCREEN_WIDTH_SCALE = 1.6


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
    Worksheet for the formatted mode: a grid of narrow columns wider than the printable width for comfortable reading
    on screen (printing fits it to the page width), merged blocks, borders, images and print settings, no gridlines.
    """

    def __init__(self, worksheet, direction, page):
        """
        Size the column grid from the page content width and apply the page print settings.
        """
        self.worksheet, self.direction, self.last_row = worksheet, direction, 0
        self.content_pixels = content_width(page) * SCREEN_WIDTH_SCALE
        self.unit_pixels = self.content_pixels / GRID_COLUMNS
        worksheet.sheet_view.showGridLines = False
        for column in range(1, GRID_COLUMNS + 1):
            worksheet.column_dimensions[get_column_letter(column)].width = round((self.unit_pixels - 5) / 7, 2)
        if page:
            self.set_page(page)

    def place(self, row, column, width, value, style=Style(), number_format=None, height=1, padding=4):
        """
        Write a value into a block of cells, merge it, style every cell of the block and fit the row height.
        """
        check_limits(row + height - 1, column + width - 1)
        for cell in self.block(row, column, width, height):
            write_value(cell, None, style, self.direction)
        write_value(self.worksheet.cell(row=row, column=column), value, style, self.direction, number_format)
        if width > 1 or height > 1:
            self.worksheet.merge_cells(start_row=row, start_column=column, end_row=row + height - 1, end_column=column + width - 1)
        if height == 1:
            self.fit_row(row, value, width, style, padding)
        self.last_row = max(self.last_row, row + height - 1)

    def outline(self, row, column, width, height, style):
        """
        Draw a component's background and border around the block it used, keeping inner cell borders.
        """
        fill, sides = get_fill(style.background_color), [get_side(side) for side in edge_borders(style)]
        for cell in self.block(row, column, width, height):
            if fill:
                cell.fill = fill
            cell.border = edge_border(cell, sides, row, column, width, height)
        self.last_row = max(self.last_row, row + height - 1)

    def block(self, row, column, width, height):
        """
        Return every cell of a block.
        """
        return [cell for cells in self.worksheet.iter_rows(min_row=row, max_row=row + height - 1, min_col=column, max_col=column + width - 1) for cell in cells]

    def fit_row(self, row, value, width, style, padding):
        """
        Grow the row so wrapped text fits, since Excel does not auto-fit merged cells.
        """
        size = style.font_size or token("--rk-font-md")
        lines = sum(max(1, math.ceil(len(line) * pixels(size) * CHARACTER_WIDTH / max(width * self.unit_pixels - 12, 8))) for line in str(value or "").split("\n"))
        self.set_row_height(row, lines * pixels(size) * 0.75 * LINE_HEIGHT + padding)

    def set_row_height(self, row, points):
        """
        Set a row height in points, keeping the tallest request.
        """
        dimension = self.worksheet.row_dimensions[row]
        dimension.height = max(dimension.height or 0, round(points, 1))
        self.last_row = max(self.last_row, row)

    def add_image(self, data, row, column, width, image_width=None, image_height=None):
        """
        Anchor an image centred in a block of columns and return its height in pixels.
        """
        image = ExcelImage(data)
        if image_width:
            image.width, image.height = image_width, image_height or round(image.height * image_width / image.width)
        offset = max(0, (width - math.ceil(image.width / self.unit_pixels)) // 2)
        self.worksheet.add_image(image, f"{get_column_letter(column + offset)}{row}")
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
        margins.top, margins.right, margins.bottom, margins.left = (millimetres(value) / 25.4 for value in (page.margin_top, page.margin_right, page.margin_bottom, page.margin_left))
        self.worksheet.sheet_properties.pageSetUpPr.fitToPage, setup.fitToWidth, setup.fitToHeight = True, 1, 0

    def finish(self):
        """
        Limit printing to the report area.
        """
        if self.last_row:
            self.worksheet.print_area = f"A1:{get_column_letter(GRID_COLUMNS)}{self.last_row}"


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


def edge_borders(style):
    """
    Return the left, right, top and bottom borders of a component style.
    """
    whole = f"{style.border_width or 1}px {style.border_style or 'solid'} {style.border_color}" if style.border_color else None
    return [side or whole for side in (style.border_left, style.border_right, style.border_top, style.border_bottom)]


def edge_border(cell, sides, row, column, width, height):
    """
    Combine a cell's own border with the outline sides that fall on the block edges.
    """
    left, right, top, bottom = sides
    current = cell.border
    return Border(
        left=left if cell.column == column and left.style else current.left,
        right=right if cell.column == column + width - 1 and right.style else current.right,
        top=top if cell.row == row and top.style else current.top,
        bottom=bottom if cell.row == row + height - 1 and bottom.style else current.bottom,
    )


def content_width(page):
    """
    Return the printable width of a page in pixels (A4 portrait with 15 mm margins when there is no Page).
    """
    if page is None:
        return (210 - 30) * PIXELS_PER_MILLIMETRE
    width, height = PAPER_MILLIMETRES.get(page.size, (210, 297))
    paper = height if page.orientation == "landscape" else width
    return (paper - millimetres(page.margin_left) - millimetres(page.margin_right)) * PIXELS_PER_MILLIMETRE


def millimetres(value):
    """
    Convert a CSS length such as "12mm" to millimetres.
    """
    factor = {"mm": 1, "cm": 10, "in": 25.4, "pt": 25.4 / 72}.get(str(value)[-2:])
    if factor is None:
        raise ExcelExportError(f"Page margin {value!r} must use mm, cm, in or pt.")
    return float(value[:-2]) * factor
