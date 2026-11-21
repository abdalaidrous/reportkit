from dataclasses import dataclass
from .....components.table import TableCell
from .....formatting.cells import TableCellFormatter
from .....styles.style import Style
from ...direction import text_direction


@dataclass(frozen=True, kw_only=True)
class HtmlTableCell:
    """
    Hold a prepared HTML table cell.
    """

    display: str = ""
    content: str | None = None
    css_class: str = ""
    style: str = ""
    colspan: int = 1
    rowspan: int = 1

    @property
    def lines(self):
        """
        Split display text into lines with their text directions.
        """
        return [(line, text_direction(line)) for line in self.display.split("\n")]


class TableCellRenderer:
    """
    Prepare table cells for HTML rendering.
    """

    def render(self, value, column, context, engine):
        """
        Render a value using its column definition.
        """
        if isinstance(value, TableCell):
            return self.render_cell(value, context, engine, column)
        formatted = TableCellFormatter.format(value, column)
        return self.build(display=formatted.display, align=formatted.align, column=column, tone=formatted.tone, engine=engine)

    def render_cell(self, cell, context, engine, column=None):
        """
        Render an explicit table cell.
        """
        content = "".join(engine.render(child, context) for child in cell.children) if cell.children else None
        display = "" if cell.value is None else str(cell.value)
        align = cell.align or (column.align if column else "start")
        return self.build(display=display, content=content, align=align, column=column, style=cell.style, colspan=cell.colspan, rowspan=cell.rowspan, engine=engine)

    @classmethod
    def build(cls, display, align, column, engine, content=None, tone=None, style=None, colspan=1, rowspan=1):
        """
        Build the prepared HTML table cell.
        """
        return HtmlTableCell(display=display, content=content, css_class=cls.get_class(column, tone), style=cls.get_style(align, column, style, engine), colspan=colspan, rowspan=rowspan)

    @staticmethod
    def get_class(column, tone=None):
        """
        Get the table cell CSS classes.
        """
        classes = ["rk-table-cell"]
        if tone:
            classes.append(f"rk-table-cell--{tone}")
        if column and column.nowrap:
            classes.append("rk-table-cell--nowrap")
        return " ".join(classes)

    @staticmethod
    def get_style(align, column, style, engine):
        """
        Get the resolved table cell style.
        """
        base = Style(text_align=align, vertical_align=column.vertical_align if column else None)
        return engine.styles.resolve(base.merge(style) if style else base)