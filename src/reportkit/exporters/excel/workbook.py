from io import BytesIO

from openpyxl import Workbook

from ...components.document import Page
from .exceptions import ExcelExportError
from .exporter import INVALID_SHEET_NAME
from .renderers import DATA_RENDERERS, FORMATTED_RENDERERS
from .renderers.base import Region
from .values import cell_value
from .styles import pixels
from .worksheet import GRID_COLUMNS, DataSheet, FormattedSheet, edge_borders


class ExcelWorkbook:
    """
    Own the openpyxl workbook: create it (standard or streaming), name its sheets and save it to bytes.
    """

    def __init__(self, options, context, title):
        """
        Create the workbook; streaming uses openpyxl's write-only mode.
        """
        self.options, self.direction, self.names = options, context.direction, set()
        self.book = Workbook(write_only=options.streaming)
        if not options.streaming:
            self.book.remove(self.book.active)
        self.book.properties.title = title or None

    def create_sheet(self, name):
        """
        Create a worksheet with a unique valid name and the report direction.
        """
        worksheet = self.book.create_sheet(self.unique_name(name))
        worksheet.sheet_view.rightToLeft = self.direction == "rtl"
        return worksheet

    def unique_name(self, name):
        """
        Make a derived sheet name valid and unique.
        """
        base = INVALID_SHEET_NAME.sub(" ", name).strip(" '")[:31] or "Sheet"
        candidate, number = base, 2
        while candidate.lower() in self.names:
            candidate, number = f"{base[:27]} ({number})", number + 1
        self.names.add(candidate.lower())
        return candidate

    def close(self):
        """
        Finish a streaming workbook's open sheets after a failed export; nothing is saved, so no partial file is produced.
        """
        if self.options.streaming:
            for worksheet in self.book.worksheets:
                worksheet.close()

    def save(self):
        """
        Serialize the workbook to XLSX bytes.
        """
        buffer = BytesIO()
        try:
            self.book.save(buffer)
        except (OSError, ValueError, TypeError) as error:
            raise ExcelExportError(f"Could not write the XLSX file: {error}") from error
        return buffer.getvalue()


class FormattedEngine:
    """
    Lay the report out on one page-wide sheet like the HTML/PDF output, with margins, outlines and print settings.
    """

    def __init__(self, workbook, context, document):
        """
        Create the report sheet sized to the first page of the document.
        """
        page = next(find_components(document, Page), None)
        self.sheet, self.options = FormattedSheet(workbook.create_sheet(workbook.options.sheet_name), context.direction, page), workbook.options

    def write(self, document, context):
        """
        Render the document across the whole column grid.
        """
        self.render(document, context, Region(1, 1, GRID_COLUMNS))
        self.sheet.finish()

    def render(self, component, context, region):
        """
        Render one component with its vertical margins, outline and background, and return the rows it used.
        """
        style = context.resolve_style(component)
        top = self.add_gap(region.row, style.margin_top)
        height = FORMATTED_RENDERERS.get(component).render(component, context, self, region.below(top))
        if height and (style.background_color or edge_borders(style) != [None] * 4):
            self.sheet.outline(region.row + top, region.column, region.width, height, style)
        return top + height + self.add_gap(region.row + top + height, style.margin_bottom)

    def add_gap(self, row, margin):
        """
        Turn a vertical CSS margin into an empty row of the same height.
        """
        if not margin or pixels(margin) < 4:
            return 0
        self.sheet.set_row_height(row, pixels(margin) * 0.75)
        return 1

    def value(self, value):
        """
        Convert a report value for Excel using the configured decimal policy.
        """
        return cell_value(value, self.options.decimal_policy)


class DataEngine:
    """
    Write analysis-ready sheets: report information rows, then one typed sheet per table, append-only for streaming.
    """

    def __init__(self, workbook, context):
        """
        Prepare lazy sheet creation.
        """
        self.workbook, self.direction, self.options, self.information, self.tables = workbook, context.direction, workbook.options, None, 0

    def write(self, document, context):
        """
        Render the document.
        """
        self.render(document, context)

    def render(self, component, context):
        """
        Render one component.
        """
        DATA_RENDERERS.get(component).render(component, context, self)

    def information_sheet(self):
        """
        Return the sheet holding texts and key/value pairs, created on first use.
        """
        if self.information is None:
            self.information = DataSheet(self.workbook.create_sheet(self.options.sheet_name), self.direction)
        return self.information

    def table_sheet(self, table):
        """
        Create the sheet for one table, named after its caption.
        """
        self.tables += 1
        return DataSheet(self.workbook.create_sheet(table.header or f"Table {self.tables}"), self.direction)

    def value(self, value):
        """
        Convert a report value for Excel using the configured decimal policy.
        """
        return cell_value(value, self.options.decimal_policy)


def find_components(component, kind):
    """
    Yield the components of one type in the tree without touching table rows.
    """
    if isinstance(component, kind):
        yield component
    for child in getattr(component, "children", []):
        yield from find_components(child, kind)
