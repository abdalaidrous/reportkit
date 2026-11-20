from .document import Report, Page, Header, Footer
from .layout import Section, Row, Column, Grid, Spacer, Divider
from .text import Text, Heading
from .table import Table
from .media import Image, Chart
from .pagination import PageBreak, PageNumber, PageCount
from ..core.registry import ComponentRegistry


COMPONENT_TYPES = {
    "report": Report,
    "page": Page,
    "header": Header,
    "footer": Footer,
    "section": Section,
    "row": Row,
    "column": Column,
    "grid": Grid,
    "spacer": Spacer,
    "divider": Divider,
    "text": Text,
    "heading": Heading,
    "table": Table,
    "image": Image,
    "chart": Chart,
    "page_break": PageBreak,
    "page_number": PageNumber,
    "page_count": PageCount,
}

for name, component in COMPONENT_TYPES.items():
    ComponentRegistry.register(name, component)
