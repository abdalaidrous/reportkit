from collections.abc import Iterable, Iterator, Mapping
from typing import Any

from ..components.table import Table, TableColumn, TableRow, TableStyle
from ..styles.style import Style


RowSource = Iterable[TableRow | Mapping[str, Any]]


class PreparedRows:
    """
    Wrap prepared rows as TableRow instances lazily, re-reading the source on every iteration.
    """

    def __init__(self, rows: RowSource):
        """
        Keep the source without consuming it.
        """
        if not isinstance(rows, Iterable):
            raise TypeError("Table rows must be iterable.")
        self.rows = rows

    def __iter__(self) -> Iterator[TableRow]:
        """
        Yield each source row as a TableRow.
        """
        return map(as_row, self.rows)


def as_row(row: TableRow | Mapping[str, Any], kind: str = "data") -> TableRow:
    """
    Return a TableRow, wrapping a mapping of prepared values.
    """
    if isinstance(row, TableRow):
        return row
    if isinstance(row, Mapping):
        return TableRow(values=row, kind=kind)
    raise TypeError("Table rows must be TableRow instances or mappings.")


class TableBuilder:
    """
    Build a Table step by step from prepared columns, rows and totals; nothing is calculated here.
    """

    def __init__(self):
        """
        Start an empty table definition.
        """
        self._columns: list[TableColumn] = []
        self._rows: RowSource = ()
        self._totals: TableRow | None = None
        self._title: str | None = None
        self._style = Style()
        self._table_style = TableStyle()

    def column(self, key: str, title: str, **options) -> "TableBuilder":
        """
        Append one column; options are the TableColumn fields.
        """
        self._columns.append(TableColumn(key=key, title=title, **options))
        return self

    def columns(self, *columns: TableColumn) -> "TableBuilder":
        """
        Append ready TableColumn instances.
        """
        self._columns.extend(columns)
        return self

    def rows(self, rows: RowSource) -> "TableBuilder":
        """
        Set the prepared rows; mappings become TableRow instances as they are read.
        """
        self._rows = rows
        return self

    def totals(self, totals: TableRow | Mapping[str, Any] | None) -> "TableBuilder":
        """
        Set the prepared footer row shown as the table total.
        """
        self._totals = None if totals is None else as_row(totals, kind="total")
        return self

    def title(self, title: str | None) -> "TableBuilder":
        """
        Set the table caption.
        """
        self._title = title
        return self

    def style(self, style: Style) -> "TableBuilder":
        """
        Set the table component style.
        """
        self._style = style
        return self

    def table_style(self, table_style: TableStyle | None = None, **options) -> "TableBuilder":
        """
        Set the table presentation, from a TableStyle or from its fields.
        """
        if table_style is not None and options:
            raise TypeError("Pass either a TableStyle or its fields, not both.")
        self._table_style = table_style if table_style is not None else TableStyle(**options)
        return self

    def build(self) -> Table:
        """
        Create the validated Table.
        """
        return Table(
            columns=list(self._columns),
            rows=PreparedRows(self._rows),
            header=self._title,
            footer=self._totals,
            style=self._style,
            table_style=self._table_style,
        )
