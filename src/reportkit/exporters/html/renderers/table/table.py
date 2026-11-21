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
        rows = self.prepare_rows(component.rows, component.columns, engine)
        footer = self.prepare_row(component.footer, component.columns, engine) if component.footer else None
        return engine.templates.render(self.template_name, columns=component.columns, rows=rows, footer=footer, header=component.header, table_style=component.table_style, style=style)

    def prepare_rows(self, rows, columns, engine):
        """Yield formatted table rows lazily."""
        for row in rows:
            yield self.prepare_row(row, columns, engine)

    def prepare_row(self, row, columns, engine):
        """Prepare one externally supplied row."""
        if not isinstance(row, TableRow):
            raise TypeError("Table rows must be TableRow instances.")
        cells = [self.prepare_explicit_cell(cell, engine) for cell in row.cells] if row.cells is not None else [self.prepare_column_cell(row.values.get(column.key), column, engine) for column in columns]
        return {"kind": row.kind, "cells": cells, "style": engine.styles.resolve(row.style)}

    def prepare_column_cell(self, value, column, engine):
        """Format a value using its column definition."""
        formatted = TableCellFormatter.format(value, column)
        style_values = {"vertical_align": column.vertical_align}
        if formatted.color:
            style_values["color"] = formatted.color
        return FormattedTableCell(display=formatted.display, align=formatted.align, style=engine.styles.resolve(Style(**style_values)))

    def prepare_explicit_cell(self, cell, engine):
        """Prepare an explicitly defined table cell."""
        if not isinstance(cell, TableCell):
            raise TypeError("Explicit table cells must be TableCell instances.")
        return FormattedTableCell(display="" if cell.value is None else str(cell.value), align=cell.align, colspan=cell.colspan, rowspan=cell.rowspan, style=engine.styles.resolve(cell.style))
