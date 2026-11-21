from ....components.document import Report
from ....components.layout import Column, Row, Section
from ....components.text import Heading, Text
from ..registry import HtmlRendererRegistry
from .document import ReportRenderer
from .layout import ColumnRenderer, RowRenderer, SectionRenderer
from .text import HeadingRenderer, TextRenderer


HtmlRendererRegistry.register(Report, ReportRenderer)
HtmlRendererRegistry.register(Section, SectionRenderer)
HtmlRendererRegistry.register(Row, RowRenderer)
HtmlRendererRegistry.register(Column, ColumnRenderer)
HtmlRendererRegistry.register(Text, TextRenderer)
HtmlRendererRegistry.register(Heading, HeadingRenderer)
