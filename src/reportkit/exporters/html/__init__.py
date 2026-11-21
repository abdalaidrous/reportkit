from . import renderers
from .exporter import HtmlExporter
from ..registry import ExporterRegistry


ExporterRegistry.register("html", HtmlExporter)
