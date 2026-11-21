from io import BytesIO

from openpyxl import Workbook

from ...components.table import Table
from .exceptions import ExcelExportError
from .exporter import INVALID_SHEET_NAME
from .renderers import DATA_RENDERERS, FORMATTED_RENDERERS
from .renderers.base import Region
from .values import cell_value
from .worksheet import DataSheet, FormattedSheet


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
    Lay the report out on one sheet like the HTML/PDF output, with merged cells, styles and print settings.
    """

    def __init__(self, workbook, context, document):
        """
        Create the report sheet and measure its column grid from the tables.
        """
        self.sheet, self.options = FormattedSheet(workbook.create_sheet(workbook.options.sheet_name), context.direction), workbook.options
        self.width = max((len(table.columns) for table in find_tables(document)), default=6)

    def write(self, document, context):
        """
        Render the document from the top-left cell.
        """
        self.render(document, context, Region(1, 1, self.width))
        self.sheet.finish()

    def render(self, component, context, region):
        """
        Render one component in a region and return the rows it used.
        """
        return FORMATTED_RENDERERS.get(component).render(component, context, self, region)

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


def find_tables(component):
    """
    Yield the tables of the component tree without touching their rows.
    """
    if isinstance(component, Table):
        yield component
    for child in getattr(component, "children", []):
        yield from find_tables(child)
