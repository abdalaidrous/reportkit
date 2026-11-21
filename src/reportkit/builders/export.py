from importlib import import_module
from os import PathLike
from pathlib import Path
from typing import BinaryIO

from ..components.document import Report
from ..exporters.registry import ExporterRegistry
from ..rendering.context import RenderingContext


class ReportExport:
    """
    Export a Report by format name, loading the exporter package that registers it on first use.
    """

    PACKAGES = {
        "html": "html",
        "pdf": "pdf",
        "excel": "excel",
        "xlsx": "excel",
        "word": "word",
        "docx": "word",
    }

    @classmethod
    def export(cls, report: Report, format: str, context: RenderingContext | None = None, **options) -> bytes:
        """
        Return the exported bytes; options go to the exporter (for example options=PdfOptions(...)).
        """
        return cls.exporter(format).export(report, context, **options)

    @classmethod
    def export_to(cls, report: Report, format: str, target: str | PathLike | BinaryIO, context: RenderingContext | None = None, **options):
        """
        Write the export to a path or a binary stream, streaming when the exporter supports it.
        """
        exporter = cls.exporter(format)
        if hasattr(exporter, "export_to"):
            return exporter.export_to(report, target, context, **options)
        content = exporter.export(report, context, **options)
        if hasattr(target, "write"):
            target.write(content)
        else:
            Path(target).write_bytes(content)
        return target

    @classmethod
    def exporter(cls, format: str):
        """
        Create the exporter registered for the format.
        """
        package = cls.PACKAGES.get(format)
        if package is not None:
            import_module(f"..exporters.{package}", __package__)
        return ExporterRegistry.get(format)()
