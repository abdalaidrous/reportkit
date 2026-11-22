from contextlib import suppress
from tempfile import TemporaryFile

from openpyxl import Workbook

from ..exceptions import ExcelExportError
from ..exporter import INVALID_SHEET_NAME
from .styles import copy_with_apply_flags


class ExcelWorkbook:
    """
    Own the openpyxl workbook: create it (standard or streaming), name its sheets and save it to a path or stream.
    """

    def __init__(self, options, context, title):
        """
        Create the workbook; streaming uses openpyxl's write-only mode.
        """
        self.options = options
        self.direction = context.direction
        self.names = set()
        self.book = self.create_workbook(title)

    def create_workbook(self, title):
        """
        Create the workbook and remove its default sheet when not streaming.
        """
        book = Workbook(write_only=self.options.streaming)
        if not self.options.streaming:
            book.remove(book.active)
        book.properties.title = title or None
        return book

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
        base = self.clean_name(name)
        candidate, number = base, 2
        while candidate.lower() in self.names:
            candidate = self.numbered_name(base, number)
            number += 1
        self.names.add(candidate.lower())
        return candidate

    @staticmethod
    def clean_name(name):
        """
        Remove invalid sheet name characters and limit the name to Excel's maximum length.
        """
        return INVALID_SHEET_NAME.sub(" ", name).strip(" '")[:31] or "Sheet"

    @staticmethod
    def numbered_name(base, number):
        """
        Append a numeric suffix while keeping the sheet name within Excel's length limit.
        """
        suffix = f" ({number})"
        return base[:31 - len(suffix)] + suffix

    def close(self):
        """
        Finish a streaming workbook's open sheets after a failed export without hiding the export error; nothing is
        saved, so no partial file is produced.
        """
        if not self.options.streaming:
            return
        for worksheet in self.book.worksheets:
            with suppress(Exception):
                worksheet.close()

    def save(self, target):
        """
        Serialize the workbook to a temporary file, then copy it to the target with the cell format flags fixed.
        """
        try:
            with TemporaryFile() as spool:
                self.save_to_spool(spool)
                copy_with_apply_flags(spool, target)
        except (OSError, ValueError, TypeError) as error:
            raise ExcelExportError(f"Could not write the XLSX file: {error}") from error

    def save_to_spool(self, spool):
        """
        Save the workbook to a temporary file and rewind it for the final XLSX copy.
        """
        self.book.save(spool)
        spool.seek(0)
