from dataclasses import dataclass

from .....components.table import TableCell
from .....formatting.cells import TableCellFormatter
from .....styles.style import Style


@dataclass(frozen=True, kw_only=True)
class HtmlTableCell:
    """Hold one cell ready for cell.html: escaped text or pre-rendered component HTML."""

    display: str = ""
    content: str | None = None
    css_class: str = ""
    style: str = ""
    colspan: int = 1
    rowspan: int = 1


class TableCellRenderer:
    """Prepare table cells; TableCell children render through the engine, plain values through TableCellFormatter."""

    def render(self, value, column, context, engine):
        """Prepare a row value for its column."""
        if isinstance(value, TableCell):
            return self.render_cell(value, context, engine, column)
        formatted = TableCellFormatter.format(value, column)
        return self.build(display=formatted.display, align=formatted.align, column=column, tone=formatted.tone, engine=engine)

    def render_cell(self, cell, context, engine, column=None):
        """Prepare an explicit TableCell, rendering its children when present."""
        content = "".join(engine.render(child, context) for child in cell.children) if cell.children else None
        display = "" if cell.value is None else str(cell.value)
        align = cell.align or (column.align if column else "start")
        return self.build(display=display, content=content, align=align, column=column, style=cell.style, colspan=cell.colspan, rowspan=cell.rowspan, engine=engine)

    @staticmethod
    def build(display, align, column, engine, content=None, tone=None, style=None, colspan=1, rowspan=1):
        """Resolve the cell classes and inline style."""
        classes = ["rk-table-cell", f"rk-table-cell--{tone}" if tone else "", "rk-table-cell--nowrap" if column and column.nowrap else ""]
        base = Style(text_align=align, vertical_align=column.vertical_align if column else None)
        css = engine.styles.resolve(base.merge(style) if style else base)
        return HtmlTableCell(display=display, content=content, css_class=" ".join(c for c in classes if c), style=css, colspan=colspan, rowspan=rowspan)
