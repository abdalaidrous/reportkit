from collections.abc import Iterable
from os import PathLike
from typing import BinaryIO

from ..components.document import Footer, Header, Page, Report
from ..components.layout import Spacer
from ..components.media import Chart, ChartSeries, QRCode
from ..components.pagination import PageBreak, PageCount, PageNumber
from ..components.table import TableColumn
from ..core.component import Component
from ..rendering.context import RenderingContext
from ..styles.style import Style
from .export import ReportExport
from .table import RowSource, TableBuilder


class ReportBuilder:
    """
    Build a single-page report with ordered components and prepared data.
    """

    def __init__(self, title: str = "", *, style: Style | None = None):
        """
        Initialize the report builder.
        """
        self._title = title
        self._style = style or Style()
        self._page: dict = {}
        self._header: Header | None = None
        self._footer: Footer | None = None
        self._content: list[Component] = []
        self._page_number: PageNumber | None = None

    def page(self, *, margin: str | None = None, **settings) -> "ReportBuilder":
        """
        Configure page settings and optional margin shorthand.
        """
        if margin is not None:
            settings = {**expand_margin(margin), **settings}

        self._page.update(settings)
        return self

    def header(self, *children: Component, repeat: bool = False, style: Style | None = None) -> "ReportBuilder":
        """
        Configure the report header.
        """
        self._header = Header(children=list(children), repeat=repeat, style=style or Style())
        return self

    def footer(self, *children: Component, repeat: bool = False, style: Style | None = None) -> "ReportBuilder":
        """
        Configure the report footer.
        """
        self._footer = Footer(children=list(children), repeat=repeat, style=style or Style())
        return self

    def add(self, *components: Component) -> "ReportBuilder":
        """
        Append components to the report content.
        """
        self._content.extend(components)
        return self

    def table(self, columns: Iterable[TableColumn], rows: RowSource = (), *, totals=None, title: str | None = None, style: Style | None = None, table_style=None) -> "ReportBuilder":
        """
        Append a table with prepared rows and optional totals.
        """
        builder = self.create_table(columns, rows, totals, title)
        self.configure_table(builder, style, table_style)
        return self.add(builder.build())

    @staticmethod
    def create_table(columns, rows, totals, title):
        """
        Initialize a table builder with prepared data.
        """
        return TableBuilder().columns(*columns).rows(rows).totals(totals).title(title)

    @staticmethod
    def configure_table(builder, style, table_style):
        """
        Apply optional table and component styles.
        """
        if style is not None:
            builder.style(style)

        if table_style is not None:
            builder.table_style(table_style)

    def spacer(self, height: float) -> "ReportBuilder":
        """
        Append vertical spacing.
        """
        return self.add(Spacer(height=height))

    def page_break(self) -> "ReportBuilder":
        """
        Append a forced page break.
        """
        return self.add(PageBreak())

    def chart(self, labels: list[str], series: Iterable[ChartSeries], *, chart_type: str = "bar", **options) -> "ReportBuilder":
        """
        Append a bar, line or pie chart of prepared values; options are the other Chart fields (title, width, ...).
        """
        return self.add(Chart(labels=list(labels), series=list(series), chart_type=chart_type, **options))

    def qr_code(self, value: str, **options) -> "ReportBuilder":
        """
        Append a QR code of a prepared value; options are the other QRCode fields (size, error_correction, ...).
        """
        return self.add(QRCode(value=value, **options))

    def page_count(self, format: str = "{pages}", *, style: Style | None = None) -> "ReportBuilder":
        """
        Append a line with the total number of printed pages.
        """
        return self.add(PageCount(format=format, style=style or Style()))

    def page_number(self, format: str = "Page {page} of {pages}") -> "ReportBuilder":
        """
        Configure the page number format.
        """
        self._page_number = PageNumber(format=format)
        return self

    def build(self) -> Report:
        """
        Build the report with its configured page.
        """
        page = Page(children=self._children(), **self._page)
        return Report(title=self._title, style=self._style, children=[page])

    def export(self, format: str, context: RenderingContext | None = None, **options) -> bytes:
        """
        Build and export the report as bytes.
        """
        return ReportExport.export(self.build(), format, context, **options)

    def export_to(self, format: str, target: str | PathLike | BinaryIO, context: RenderingContext | None = None, **options):
        """
        Build and export the report to a path or binary stream.
        """
        return ReportExport.export_to(self.build(), format, target, context, **options)

    def _children(self) -> list[Component]:
        """
        Assemble page components in their required order.
        """
        children = []

        if self._header is not None:
            children.append(self._header)

        if self._footer is not None and self._footer.repeat:
            children.append(self._footer)

        children.extend(self._content)

        if self._footer is not None and not self._footer.repeat:
            children.append(self._footer)

        if self._page_number is not None:
            children.append(self._page_number)

        return children


def expand_margin(margin: str) -> dict[str, str]:
    """
    Expand CSS margin shorthand into individual page margins.
    """
    values = margin.split()

    if not 1 <= len(values) <= 4:
        raise ValueError("Margin shorthand takes one to four values.")

    top = values[0]
    right = values[1] if len(values) > 1 else top
    bottom = values[2] if len(values) > 2 else top
    left = values[3] if len(values) > 3 else right

    return {"margin_top": top, "margin_right": right, "margin_bottom": bottom, "margin_left": left}