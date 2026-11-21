from ....components.document import Report
from ....components.layout import Column, Divider, Grid, Row, Section, Spacer
from ....components.table import Table
from ....components.text import Heading, Text
from ..registry import HtmlRendererRegistry
from .divider import DividerRenderer
from .document import ReportRenderer
from .grid import GridRenderer
from .layout import ColumnRenderer, RowRenderer, SectionRenderer
from .spacer import SpacerRenderer
from .table import TableRenderer
from .text import HeadingRenderer, TextRenderer


HtmlRendererRegistry.register(Report, ReportRenderer)
HtmlRendererRegistry.register(Section, SectionRenderer)
HtmlRendererRegistry.register(Row, RowRenderer)
HtmlRendererRegistry.register(Column, ColumnRenderer)
HtmlRendererRegistry.register(Grid, GridRenderer)
HtmlRendererRegistry.register(Spacer, SpacerRenderer)
HtmlRendererRegistry.register(Divider, DividerRenderer)
HtmlRendererRegistry.register(Table, TableRenderer)
HtmlRendererRegistry.register(Text, TextRenderer)
HtmlRendererRegistry.register(Heading, HeadingRenderer)
