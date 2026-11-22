from ....components.document import Footer, Header, Page, Report
from ....components.information import InfoGrid, KeyValue
from ....components.layout import Box, Column, Divider, Grid, Row, Section, Spacer
from ....components.media import Chart, Image, QRCode
from ....components.pagination import PageBreak, PageCount, PageNumber
from ....components.table import Table
from ....components.typography import Heading, RichText, Text
from .chart import ChartRenderer
from .information import KeyValueRenderer
from .layout import ColumnsRenderer, DividerRenderer, FooterRenderer, GridRenderer, HeaderRenderer, InfoGridRenderer, PageBreakRenderer, PageCountRenderer, PageNumberRenderer, SpacerRenderer, StackRenderer
from .media import ImageRenderer, QRCodeRenderer
from .registry import WordRendererRegistry
from .table import TableRenderer
from .text import TextRenderer

WORD_RENDERERS = WordRendererRegistry({
    **{component: StackRenderer() for component in (Report, Page, Section, Box, Column)},
    **{component: TextRenderer() for component in (Text, Heading, RichText)},
    Header: HeaderRenderer(), Footer: FooterRenderer(),
    Row: ColumnsRenderer(), Grid: GridRenderer(), InfoGrid: InfoGridRenderer(),
    KeyValue: KeyValueRenderer(), Table: TableRenderer(), Image: ImageRenderer(), QRCode: QRCodeRenderer(), Chart: ChartRenderer(),
    Spacer: SpacerRenderer(), Divider: DividerRenderer(), PageBreak: PageBreakRenderer(), PageNumber: PageNumberRenderer(), PageCount: PageCountRenderer(),
})

__all__ = ["WORD_RENDERERS", "WordRendererRegistry"]
