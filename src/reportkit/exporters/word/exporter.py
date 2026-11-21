from importlib import import_module
from io import BytesIO

from ...components.document import Report
from ...rendering.context import RenderingContext
from ..base import BaseExporter

PYTHON_DOCX_HELP = 'Word export requires python-docx. Install it with: pip install "reportkit[word]"'


class WordExporter(BaseExporter):
    """
    Export a report to DOCX bytes with python-docx, directly from the component tree (no HTML involved).
    """

    def export(self, document, context=None) -> bytes:
        """
        Write the report into a Word document and return the DOCX bytes.
        """
        buffer = BytesIO()
        self.export_to(document, buffer, context)
        return buffer.getvalue()

    def export_to(self, document, target, context=None):
        """
        Write the DOCX to a file path or a binary stream; finished table rows wait on disk, not in memory.
        """
        if not isinstance(document, Report):
            raise TypeError("Word export requires a Report component.")
        context = context or RenderingContext()
        self.load_document_module().WordEngine(document, context).write(document, context, target)

    @staticmethod
    def load_document_module():
        """
        Import the python-docx based writer lazily so python-docx stays an optional dependency.
        """
        try:
            return import_module(".document", __package__)
        except ImportError as error:
            raise ImportError(PYTHON_DOCX_HELP) from error
