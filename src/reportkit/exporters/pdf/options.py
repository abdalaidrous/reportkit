from dataclasses import dataclass

from .exceptions import PdfExportError


@dataclass(frozen=True, kw_only=True)
class PdfOptions:
    """
    Choose how a PDF is laid out: reports whose page-level tables have more than chunk_rows rows are laid out in
    chunks of about chunk_rows rows, so memory stays bounded by the chunk instead of the whole report.

    workers > 1 lays chunks out in parallel processes: several times faster, but each chunk ends on its own last page,
    so pages at chunk boundaries are not filled the way a single pass fills them. The default (1) keeps the layout.
    """

    chunk_rows: int | None = 500
    workers: int = 1

    def __post_init__(self):
        """
        Reject invalid options before any layout starts; chunk_rows=None lays the whole report out in one pass.
        """
        if self.chunk_rows is not None and not self.is_positive(self.chunk_rows):
            raise PdfExportError(f"chunk_rows must be a positive integer or None, got {self.chunk_rows!r}.")
        if not self.is_positive(self.workers):
            raise PdfExportError(f"workers must be a positive integer, got {self.workers!r}.")
        if self.workers > 1 and self.chunk_rows is None:
            raise PdfExportError("workers > 1 lays chunks out in parallel and needs chunk_rows.")

    @staticmethod
    def is_positive(value):
        """
        Return whether the value is a positive integer (bool excluded).
        """
        return isinstance(value, int) and not isinstance(value, bool) and value > 0
