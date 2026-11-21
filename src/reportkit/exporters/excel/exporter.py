import re
from dataclasses import dataclass
from importlib import import_module

from ...components.document import Report
from ...rendering.context import RenderingContext
from ..base import BaseExporter
from .exceptions import ExcelExportError

OPENPYXL_HELP = 'Excel export requires openpyxl (and Pillow for images). Install it with: pip install "reportkit[excel]"'
INVALID_SHEET_NAME = re.compile(r"[\[\]:*?/\\]")


@dataclass(frozen=True, kw_only=True)
class ExcelOptions:
    """
    Choose the Excel presentation: "formatted" mirrors the HTML/PDF layout, "data" writes analysis-ready sheets.
    """

    mode: str = "formatted"
    streaming: bool = False
    sheet_name: str = "Report"
    decimal_policy: str = "error"

    def __post_init__(self):
        """
        Reject invalid or conflicting options before any sheet is written.
        """
        if self.mode not in ("formatted", "data"):
            raise ExcelExportError(f"Excel mode must be 'formatted' or 'data', got {self.mode!r}.")
        if self.mode == "formatted" and self.streaming:
            raise ExcelExportError("The formatted mode merges cells and writes them out of order, which streaming (write-only) workbooks cannot do; use mode='data' for streaming.")
        if self.decimal_policy not in ("error", "text"):
            raise ExcelExportError("decimal_policy must be 'error' or 'text'.")
        if not self.sheet_name or len(self.sheet_name) > 31 or INVALID_SHEET_NAME.search(self.sheet_name) or self.sheet_name.strip("'") != self.sheet_name:
            raise ExcelExportError(f"Invalid Excel sheet name {self.sheet_name!r}: use 1-31 characters without [ ] : * ? / \\ and no leading or trailing apostrophe.")


class ExcelExporter(BaseExporter):
    """
    Export a report to XLSX bytes with openpyxl, directly from the component tree (no HTML involved).
    """

    def export(self, document, context=None, options=None) -> bytes:
        """
        Write the report in the chosen mode and return the XLSX bytes.
        """
        if not isinstance(document, Report):
            raise TypeError("Excel export requires a Report component.")
        workbook_module, context, options = self.load_workbook_module(), context or RenderingContext(), options or ExcelOptions()
        workbook = workbook_module.ExcelWorkbook(options, context, document.title)
        engine = workbook_module.FormattedEngine(workbook, context, document) if options.mode == "formatted" else workbook_module.DataEngine(workbook, context)
        try:
            engine.write(document, context)
        except BaseException:
            workbook.close()
            raise
        return workbook.save()

    @staticmethod
    def load_workbook_module():
        """
        Import the openpyxl-based writer lazily so openpyxl stays an optional dependency.
        """
        try:
            return import_module(".workbook", __package__)
        except ImportError as error:
            raise ImportError(OPENPYXL_HELP) from error
