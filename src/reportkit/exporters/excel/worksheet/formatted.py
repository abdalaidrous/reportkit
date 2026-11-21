import math
from itertools import product

from openpyxl.cell.cell import MergedCell
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.cell_range import CellRange
from openpyxl.worksheet.merge import MergedCellRange
from openpyxl.worksheet.pagebreak import Break

from ....styles.borders import edge_borders
from ....styles.style import Style
from ....styles.tokens import token
from ..styles import get_fill, get_side, pixels
from .borders import edge_border, edge_style
from .cells import apply_style, check_limits, write_value
from .constants import CHARACTER_WIDTH, GRID_COLUMNS, LINE_HEIGHT, PAPER_SIZES, SCREEN_WIDTH_SCALE
from .page import content_width, millimetres


class FormattedSheet:
    """
    Worksheet for the formatted mode: a grid of narrow columns wider than the printable width for comfortable reading
    on screen (printing fits it to the page width), merged blocks, borders, images and print settings, no gridlines.
    """

    def __init__(self, worksheet, direction, page):
        """
        Size the column grid from the page content width and apply the page print settings.
        """
        self.worksheet, self.direction, self.last_row, self.styles = worksheet, direction, 0, {}
        self.content_pixels = content_width(page) * SCREEN_WIDTH_SCALE
        self.unit_pixels = self.content_pixels / GRID_COLUMNS
        worksheet.sheet_view.showGridLines = False
        for column in range(1, GRID_COLUMNS + 1):
            worksheet.column_dimensions[get_column_letter(column)].width = round((self.unit_pixels - 5) / 7, 2)
        if page:
            self.set_page(page)

    def place(self, row, column, width, value, style=Style(), number_format=None, height=1, padding=4):
        """
        Write a value with its style into the block's first cell, merge the block (which carries the borders to its edge
        cells) and fit the row height.
        """
        check_limits(row + height - 1, column + width - 1)
        write_value(self.worksheet.cell(row=row, column=column), value, style, self.direction, self.styles, number_format)
        if width > 1 or height > 1:
            self.merge(row, column, width, height, style)
        if height == 1:
            self.fit_row(row, value, width, style, padding)
        self.last_row = max(self.last_row, row + height - 1)

    def merge(self, row, column, width, height, style):
        """
        Merge a block and give its edge cells the block's borders. openpyxl's merge_cells scans every earlier merge and
        restyles each cell, which makes long tables slow; the layout never overlaps blocks (place_cells refuses
        overlapping spans), so the range is registered directly.
        """
        self.worksheet.merged_cells.ranges.add(MergedCellRange(self.worksheet, CellRange(min_row=row, min_col=column, max_row=row + height - 1, max_col=column + width - 1).coord))
        for current_row, current_column in product(range(row, row + height), range(column, column + width)):
            if (current_row, current_column) != (row, column):
                self.add_merged_cell(current_row, current_column, edge_style(style, current_column == column, current_column == column + width - 1, current_row == row, current_row == row + height - 1))

    def add_merged_cell(self, row, column, style):
        """
        Put a covered cell of a merged block in place, carrying the block border on its edge sides.
        """
        cell = MergedCell(self.worksheet, row=row, column=column)
        self.worksheet._cells[(row, column)] = cell
        if style is not None:
            apply_style(cell, style, self.direction, self.styles)

    def outline(self, row, column, width, height, style):
        """
        Draw a component's background and border around the block it used, keeping inner cell borders.
        """
        fill, sides = get_fill(style.background_color), [get_side(side) for side in edge_borders(style)]
        for cell in self.block(row, column, width, height) if fill else self.edges(row, column, width, height):
            if fill:
                cell.fill = fill
            cell.border = edge_border(cell, sides, row, column, width, height)
        self.last_row = max(self.last_row, row + height - 1)

    def block(self, row, column, width, height):
        """
        Return every cell of a block.
        """
        return [cell for cells in self.worksheet.iter_rows(min_row=row, max_row=row + height - 1, min_col=column, max_col=column + width - 1) for cell in cells]

    def edges(self, row, column, width, height):
        """
        Return only the cells on the border of a block, so framing a long table stays proportional to its height.
        """
        last_row, last_column = row + height - 1, column + width - 1
        positions = {(row, current) for current in range(column, last_column + 1)} | {(last_row, current) for current in range(column, last_column + 1)} | {(current, column) for current in range(row, last_row + 1)} | {(current, last_column) for current in range(row, last_row + 1)}
        return [self.worksheet.cell(row=current_row, column=current_column) for current_row, current_column in sorted(positions)]

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
