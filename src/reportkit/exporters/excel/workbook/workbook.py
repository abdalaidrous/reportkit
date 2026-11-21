from contextlib import suppress
from io import BytesIO

from openpyxl import Workbook

from ..exceptions import ExcelExportError
from ..exporter import INVALID_SHEET_NAME
from .styles import with_apply_flags


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
            suffix = f" ({number})"
            candidate, number = base[:31 - len(suffix)] + suffix, number + 1
        self.names.add(candidate.lower())
        return candidate

    def close(self):
        """
        Finish a streaming workbook's open sheets after a failed export without hiding the export error; nothing is
        saved, so no partial file is produced.
        """
        if self.options.streaming:
            for worksheet in self.book.worksheets:
                with suppress(Exception):
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
        return with_apply_flags(buffer.getvalue())
