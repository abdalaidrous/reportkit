from ..registry import ExporterRegistry
from .exceptions import WordExportError
from .exporter import WordExporter

ExporterRegistry.register("word", WordExporter)
ExporterRegistry.register("docx", WordExporter)

__all__ = ["WordExportError", "WordExporter"]
