from .....components.table import TableCell, TableRow
from .....formatting.cell import FormattedTableCell
from .....formatting.cells import TableCellFormatter
from .....styles.style import Style
from ..base import BaseHtmlRenderer


class TableRenderer(BaseHtmlRenderer):
    """Render prepared table rows and cells into HTML."""

    template_name = "components/table/table.html"

    def render(self, component, context, engine):
        """Render the supplied table without aggregations."""
        style = engine.styles.resolve(context.resolve_style(component))
        rows = self.prepare_rows(component.rows, component.columns, context, engine)
        footer = self.prepare_row(component.footer, component.columns, context, engine) if component.footer else None
        return engine.templates.render(self.template_name, columns=component.columns, rows=rows, footer=footer, header=component.header, table_style=component.table_style, style=style)

    def prepare_rows(self, rows, columns, context, engine):
        """Yield formatted table rows lazily."""
        for row in rows:
            yield self.prepare_row(row, columns, context, engine)

    def prepare_row(self, row, columns, context, engine):
        """Prepare one externally supplied row."""
        if not isinstance(row, TableRow):
            raise TypeError("Table rows must be TableRow instances.")
        if row.cells is not None:
            cells = [self.prepare_explicit_cell(cell, context, engine) for cell in row.cells]
        else:
            cells = [self.prepare_value(row.values.get(column.key), column, context, engine) for column in columns]
        return {"kind": row.kind, "cells": cells, "style": engine.styles.resolve(row.style)}

    def prepare_value(self, value, column, context, engine):
        """Prepare a row value: a TableCell renders as-is, anything else is formatted by the column."""
        if isinstance(value, TableCell):
            return self.prepare_explicit_cell(value, context, engine, column)
        return self.prepare_column_cell(value, column, engine)

    def prepare_column_cell(self, value, column, engine):
        """Format a plain value using its column definition."""
        formatted = TableCellFormatter.format(value, column)
        style_values = {"vertical_align": column.vertical_align}
        if formatted.color:
            style_values["color"] = formatted.color
        return FormattedTableCell(display=formatted.display, align=formatted.align, style=engine.styles.resolve(Style(**style_values)), nowrap=column.nowrap)

    def prepare_explicit_cell(self, cell, context, engine, column=None):
        """Prepare an explicit cell, rendering its child components when present."""
        if not isinstance(cell, TableCell):
            raise TypeError("Explicit table cells must be TableCell instances.")
        content = "".join(engine.render(child, context) for child in cell.children) if cell.children else None
        align = cell.align or (column.align if column else "start")
        style = Style(vertical_align=column.vertical_align).merge(cell.style) if column else cell.style
        return FormattedTableCell(
            display="" if cell.value is None else str(cell.value),
            content=content,
            align=align,
            colspan=cell.colspan,
            rowspan=cell.rowspan,
            style=engine.styles.resolve(style),
            nowrap=column.nowrap if column else False,
        )
