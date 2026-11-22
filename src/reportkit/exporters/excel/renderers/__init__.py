from ....components.document import Footer, Header, Page, Report
from ....components.information import InfoGrid, KeyValue
from ....components.layout import Box, Column, Divider, Grid, Row, Section, Spacer
from ....components.media import Image, QRCode
from ....components.pagination import PageBreak, PageCount, PageNumber
from ....components.table import Table
from ....components.typography import Heading, RichText, Text
from .information import KeyValueDataRenderer, KeyValueRenderer
from .layout import ColumnsDataRenderer, ColumnsRenderer, DividerRenderer, GridRenderer, InfoGridRenderer, PageBreakRenderer, PageCountRenderer, PageNumberRenderer, SkipDataRenderer, SpacerRenderer, StackDataRenderer, StackRenderer
from .media import ImageRenderer, QRCodeRenderer
from .registry import ExcelRendererRegistry
from .table import TableDataRenderer, TableRenderer
from .text import TextDataRenderer, TextRenderer

STACKS = (Report, Page, Header, Footer, Section, Box, Column)
TEXTS = (Text, Heading, RichText)

FORMATTED_RENDERERS = ExcelRendererRegistry({
    **{component: StackRenderer() for component in STACKS},
    **{component: TextRenderer() for component in TEXTS},
    Row: ColumnsRenderer(), Grid: GridRenderer(), InfoGrid: InfoGridRenderer(),
    KeyValue: KeyValueRenderer(), Table: TableRenderer(), Image: ImageRenderer(), QRCode: QRCodeRenderer(),
    Spacer: SpacerRenderer(), Divider: DividerRenderer(), PageBreak: PageBreakRenderer(), PageNumber: PageNumberRenderer(), PageCount: PageCountRenderer(),
})

DATA_RENDERERS = ExcelRendererRegistry({
    **{component: StackDataRenderer() for component in STACKS},
    **{component: ColumnsDataRenderer() for component in (Row, Grid, InfoGrid)},
    **{component: TextDataRenderer() for component in TEXTS},
    **{component: SkipDataRenderer() for component in (Image, QRCode, Spacer, Divider, PageBreak, PageNumber, PageCount)},
    KeyValue: KeyValueDataRenderer(), Table: TableDataRenderer(),
})

__all__ = ["DATA_RENDERERS", "FORMATTED_RENDERERS", "ExcelRendererRegistry"]
