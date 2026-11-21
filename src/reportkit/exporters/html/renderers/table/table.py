from .....validators.table.table import TableValidator
from ...direction import text_direction
from ..base import BaseHtmlRenderer
from .cell import TableCellRenderer


class TableRenderer(BaseHtmlRenderer):
    """
    Render tables, headers and rows using TableCellRenderer.
    """

    template_name = "components/table/table.html"

    def __init__(self, cells=None):
        """
        Initialize the table cell renderer.
        """
        self.cells = cells if cells is not None else TableCellRenderer()

    def render(self, component, context, engine):
        """
        Render the table.
        """
        style = engine.styles.resolve(context.resolve_style(component))
        rows = self.prepare_rows(component, context, engine)
        footer = self.prepare_row(component.footer, component.columns, context, engine) if component.footer else None
        header = [self.prepare_header(column) for column in component.columns]
        return engine.templates.render(self.template_name, container_class=self.get_container_class(component.table_style), table_class=self.get_class(component.table_style), columns=component.columns, header=header, caption=component.header, rows=rows, footer=footer, show_header=component.table_style.show_header, style=style)

    def prepare_rows(self, component, context, engine):
        """
        Prepare table rows lazily.
        """
        for row in component.rows:
            yield self.prepare_row(row, component.columns, context, engine)

    def prepare_row(self, row, columns, context, engine):
        """
        Prepare one table row.
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
        Prepare one table header cell.
        """
        return {"title": column.title, "subtitle": column.subtitle, "title_dir": text_direction(column.title), "subtitle_dir": text_direction(column.subtitle), "align": column.header_align or column.align, "nowrap": column.nowrap}

    @staticmethod
    def get_class(table_style):
        """
        Get the table CSS classes.
        """
        flags = ("bordered", "striped", "hover", "compact", "ruled", "repeat_header", "avoid_row_break")
        names = [f"rk-table--{flag.replace('_', '-')}" for flag in flags if getattr(table_style, flag)]
        return " ".join(["rk-table", f"rk-table--layout-{table_style.layout}", *names])

    @staticmethod
    def get_container_class(table_style):
        """
        Get the table container CSS classes.
        """
        return "rk-table-container rk-table-container--ruled" if table_style.ruled else "rk-table-container"