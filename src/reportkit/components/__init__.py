from .document import Footer, Header, Page, Report
from .information import InfoGrid, KeyValue
from .layout import Box, Column, Divider, Grid, Row, Section, Spacer
from .media import Chart, Image
from .pagination import PageBreak, PageCount, PageNumber
from .table import Table, TableCell, TableColumn, TableRow, TableStyle
from .typography import Heading, RichText, Text, TextSpan
from ..core.registry import ComponentRegistry


COMPONENT_TYPES = {
    "report": Report,
    "page": Page,
    "header": Header,
    "footer": Footer,
    "section": Section,
    "box": Box,
    "row": Row,
    "column": Column,
    "grid": Grid,
    "spacer": Spacer,
    "divider": Divider,
    "text": Text,
    "heading": Heading,
    "rich_text": RichText,
    "table": Table,
    "key_value": KeyValue,
    "info_grid": InfoGrid,
    "image": Image,
    "chart": Chart,
    "page_break": PageBreak,
    "page_number": PageNumber,
    "page_count": PageCount,
}

for name, component in COMPONENT_TYPES.items():
    ComponentRegistry.register(name, component)

__all__ = [
    "Box", "Chart", "Column", "Divider", "Footer", "Grid", "Header",
    "Heading", "Image", "InfoGrid", "KeyValue", "Page", "PageBreak",
    "PageCount", "PageNumber", "Report", "Row", "Section", "Spacer",
    "RichText", "Table", "TableCell", "TableColumn", "TableRow", "TableStyle",
    "Text", "TextSpan",
]
