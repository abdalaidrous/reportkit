import re
from dataclasses import dataclass
from importlib import import_module
from io import BytesIO

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
        self.validate_mode()
        self.validate_streaming()
        self.validate_decimal_policy()
        self.validate_sheet_name()

    def validate_mode(self):
        """
        Require a supported Excel presentation mode.
        """
        if self.mode not in ("formatted", "data"):
            raise ExcelExportError(f"Excel mode must be 'formatted' or 'data', got {self.mode!r}.")

    def validate_streaming(self):
        """
        Prevent streaming when formatted output requires merged cells and out-of-order writes.
        """
        if self.mode == "formatted" and self.streaming:
            raise ExcelExportError("The formatted mode merges cells and writes them out of order, which streaming (write-only) workbooks cannot do; use mode='data' for streaming.")

    def validate_decimal_policy(self):
        """
        Require a supported policy for decimal values that Excel cannot represent safely.
        """
        if self.decimal_policy not in ("error", "text"):
            raise ExcelExportError("decimal_policy must be 'error' or 'text'.")

    def validate_sheet_name(self):
        """
        Require a valid Excel sheet name without forbidden characters or surrounding apostrophes.
        """
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
        buffer = BytesIO()
        self.export_to(document, buffer, context, options)
        return buffer.getvalue()

    def export_to(self, document, target, context=None, options=None):
        """
        Write the XLSX to a file path or a binary stream; the workbook is spooled to a temporary file, not to memory.
        """
        self.validate_document(document)
        context = context if context is not None else RenderingContext()
        options = options if options is not None else ExcelOptions()
        workbook_module = self.load_workbook_module()
        workbook = workbook_module.ExcelWorkbook(options, context, document.title)
        engine = self.create_engine(workbook_module, workbook, context, document, options)

        try:
            engine.write(document, context)
        except BaseException:
            workbook.close()
            raise

        workbook.save(target)

    @staticmethod
    def validate_document(document):
        """
        Require a Report component before starting Excel export.
        """
        if not isinstance(document, Report):
            raise TypeError("Excel export requires a Report component.")

    @staticmethod
    def create_engine(module, workbook, context, document, options):
        """
        Create the formatted or data engine according to the selected Excel presentation mode.
        """
        if options.mode == "formatted":
            return module.FormattedEngine(workbook, context, document)
        return module.DataEngine(workbook, context)

    @staticmethod
    def load_workbook_module():
        """
        Import the openpyxl-based writer lazily so openpyxl stays an optional dependency.
        """
        try:
            return import_module(".workbook", __package__)
        except ImportError as error:
            raise ImportError(OPENPYXL_HELP) from error