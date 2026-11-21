from dataclasses import dataclass

from .exceptions import PdfExportError


@dataclass(frozen=True, kw_only=True)
class PdfOptions:
    """
    Choose how a PDF is laid out: reports whose page-level tables have more than chunk_rows rows are laid out in
    chunks of about chunk_rows rows, so memory stays bounded by the chunk instead of the whole report.
    """

    chunk_rows: int | None = 500

    def __post_init__(self):
        """
        Reject an invalid chunk size before any layout starts; None lays the whole report out in one pass.
        """
        if self.chunk_rows is not None and (isinstance(self.chunk_rows, bool) or not isinstance(self.chunk_rows, int) or self.chunk_rows < 1):
            raise PdfExportError(f"chunk_rows must be a positive integer or None, got {self.chunk_rows!r}.")
