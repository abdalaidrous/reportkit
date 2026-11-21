from collections.abc import Mapping

from ....formatting.cells import TableCellFormatter
from .base import BaseHtmlRenderer


class TableRenderer(BaseHtmlRenderer):
    """
    Render formatted report tables into HTML.
    """

    template_name = "components/table.html"

    def render(self, component, context, engine) -> str:
        """
        Render table columns and formatted rows.
        """
        style = engine.styles.resolve(context.resolve_style(component))
        rows = self.prepare_rows(component)
        return engine.templates.render(
            self.template_name,
            columns=component.columns,
            rows=rows,
            style=style,
        )

    def prepare_rows(self, component):
        """
        Yield formatted table rows lazily.
        """
        for row in component.rows:
            if not isinstance(row, Mapping):
                raise TypeError("Table rows must be mappings.")

            yield [
                TableCellFormatter.format(row.get(column.key), column)
                for column in component.columns
            ]
