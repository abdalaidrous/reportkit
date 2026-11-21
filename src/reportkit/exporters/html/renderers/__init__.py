from ....components.document import Footer, Header, Page, Report
from ....components.information import InfoGrid, KeyValue
from ....components.layout import Box, Column, Divider, Grid, Row, Section, Spacer
from ....components.media import Image
from ....components.table import Table
from ....components.typography import Heading, RichText, Text
from ....components.pagination import PageBreak, PageNumber
from ..registry import HtmlRendererRegistry
from .document import FooterRenderer, HeaderRenderer, PageRenderer, ReportRenderer
from .information import InfoGridRenderer, KeyValueRenderer
from .layout import BoxRenderer, ColumnRenderer, DividerRenderer, GridRenderer, RowRenderer, SectionRenderer, SpacerRenderer
from .media import ImageRenderer
from .pagination import PageBreakRenderer, PageNumberRenderer
from .table import TableRenderer
from .typography import HeadingRenderer, RichTextRenderer, TextRenderer


HtmlRendererRegistry.register(Report, ReportRenderer)
HtmlRendererRegistry.register(Page, PageRenderer)
HtmlRendererRegistry.register(Header, HeaderRenderer)
HtmlRendererRegistry.register(Footer, FooterRenderer)
HtmlRendererRegistry.register(Section, SectionRenderer)
HtmlRendererRegistry.register(Box, BoxRenderer)
HtmlRendererRegistry.register(Row, RowRenderer)
HtmlRendererRegistry.register(Column, ColumnRenderer)
HtmlRendererRegistry.register(Grid, GridRenderer)
HtmlRendererRegistry.register(Spacer, SpacerRenderer)
HtmlRendererRegistry.register(Divider, DividerRenderer)
HtmlRendererRegistry.register(Table, TableRenderer)
HtmlRendererRegistry.register(Image, ImageRenderer)
HtmlRendererRegistry.register(KeyValue, KeyValueRenderer)
HtmlRendererRegistry.register(InfoGrid, InfoGridRenderer)
HtmlRendererRegistry.register(Text, TextRenderer)
HtmlRendererRegistry.register(Heading, HeadingRenderer)
HtmlRendererRegistry.register(RichText, RichTextRenderer)
HtmlRendererRegistry.register(PageBreak, PageBreakRenderer)
HtmlRendererRegistry.register(PageNumber, PageNumberRenderer)
