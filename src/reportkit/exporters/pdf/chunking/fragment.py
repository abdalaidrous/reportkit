from dataclasses import dataclass, fields, replace

from ....components.table import Table
from ...html.registry import HtmlRendererRegistry
from ...html.renderers.table import TableRenderer


FRAGMENT_CLASS = "rk-pdf-fragment"
CONTINUED_CLASS = "rk-pdf-fragment--continued"
CONTINUES_CLASS = "rk-pdf-fragment--continues"


@dataclass(kw_only=True)
class TableFragment(Table):
    """
    A slice of a page-level table laid out in one chunk; continued fragments start like a table resumed on a new page.
    """

    continued: bool = False
    continues: bool = False

    @classmethod
    def of(cls, table, rows, continued, last, widths=None):
        """
        Slice the table: the caption only before the first row, the footer only after the last row, the header on
        every fragment only when it repeats, and the columns locked to the widths of the first chunk when given.
        """
        values = cls.table_values(table)
        cls.apply_header(values, table, continued)
        cls.apply_columns(values, table, widths)
        cls.apply_content(values, table, rows, continued, last)
        return cls(**values, continued=continued, continues=not last)

    @staticmethod
    def table_values(table):
        """
        Copy the initialized table fields into the fragment without modifying the original table.
        """
        return {item.name: getattr(table, item.name) for item in fields(Table) if item.init}

    @staticmethod
    def apply_header(values, table, continued):
        """
        Hide the column header on continued fragments when the table does not repeat its header.
        """
        if continued and not table.table_style.repeat_header:
            values["table_style"] = replace(table.table_style, show_header=False)

    @staticmethod
    def apply_columns(values, table, widths):
        """
        Lock fragment columns to the widths measured from the first rendered chunk when available.
        """
        if widths is not None:
            values["columns"] = [replace(column, width=f"{width}px") for column, width in zip(table.columns, widths)]

    @staticmethod
    def apply_content(values, table, rows, continued, last):
        """
        Set the fragment rows, show the caption only on the first fragment and the footer only on the last.
        """
        values.update(rows=rows, header=None if continued else table.header, footer=table.footer if last else None)


class TableFragmentRenderer(TableRenderer):
    """
    Render a fragment like its table, marking the container so the chunk layout can find it and resume it.
    """

    def container_class(self, component):
        """
        Add the fragment classes to the table container classes.
        """
        classes = [super().container_class(component), FRAGMENT_CLASS]

        if component.continued:
            classes.append(CONTINUED_CLASS)

        if component.continues:
            classes.append(CONTINUES_CLASS)

        return " ".join(classes)


HtmlRendererRegistry.register(TableFragment, TableFragmentRenderer)
