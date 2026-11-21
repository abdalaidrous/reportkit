from .....validators.table.table import TableValidator
from ..base import BaseHtmlRenderer
from .cell import TableCellRenderer


class TableRenderer(BaseHtmlRenderer):
    """
    Prepare the table, its header and its rows; cells are delegated to TableCellRenderer.
    """

    template_name = "components/table/table.html"

    def __init__(self, cells=None):
        """
        Use the given cell renderer or the default one.
        """
        self.cells = cells if cells is not None else TableCellRenderer()

    def render(self, component, context, engine):
        """
        Render the table; rows are prepared lazily while the template iterates.
        """
        style = engine.styles.resolve(context.resolve_style(component))
        rows = self.prepare_rows(component, context, engine)
        footer = self.prepare_row(component.footer, component.columns, context, engine) if component.footer else None
        header = [self.prepare_header(column) for column in component.columns]
        return engine.templates.render(self.template_name, container_class="rk-table-container rk-table-container--ruled" if component.table_style.ruled else "rk-table-container", table_class=self.table_class(component.table_style), columns=component.columns, header=header, caption=component.header, rows=rows, footer=footer, show_header=component.table_style.show_header, style=style)

    def prepare_rows(self, component, context, engine):
        """
        Yield rows one by one without materializing the iterable.
        """
        for row in component.rows:
            yield self.prepare_row(row, component.columns, context, engine)

    def prepare_row(self, row, columns, context, engine):
        """
        Prepare one row from its explicit cells or its values.
        """
        TableValidator.validate_row(row)
        if row.cells is not None:
            cells = [self.cells.render_cell(cell, context, engine) for cell in row.cells]
        else:
            cells = [self.cells.render(row.values.get(column.key), column, context, engine) for column in columns]
        return {"css_class": f"rk-table-row rk-table-{row.kind}", "style": engine.styles.resolve(row.style), "cells": cells}

    @staticmethod
    def prepare_header(column):
        """
        Prepare one header cell.
        """
        return {"title": column.title, "subtitle": column.subtitle, "align": column.header_align or column.align, "nowrap": column.nowrap}

    @staticmethod
    def table_class(table_style):
        """
        Build the table classes from its style options.
        """
        flags = ("bordered", "striped", "hover", "compact", "ruled", "repeat_header", "avoid_row_break")
        names = [f"rk-table--{flag.replace('_', '-')}" for flag in flags if getattr(table_style, flag)]
        return " ".join(["rk-table", f"rk-table--layout-{table_style.layout}", *names])
