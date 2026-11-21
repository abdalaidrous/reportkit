from ....components.document import Report
from ....components.text import Text
from ..registry import HtmlRendererRegistry
from .document import ReportRenderer
from .text import TextRenderer


HtmlRendererRegistry.register(Report, ReportRenderer)
HtmlRendererRegistry.register(Text, TextRenderer)
