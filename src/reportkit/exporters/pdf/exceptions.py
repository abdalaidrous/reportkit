class PdfExportError(RuntimeError):
    """
    Raised when a report cannot be converted to a complete PDF; the original error is kept as the cause.
    """
