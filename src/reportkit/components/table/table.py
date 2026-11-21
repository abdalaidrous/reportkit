from collections.abc import Iterable
from dataclasses import dataclass, field

from ...core.component import Component
from .column import TableColumn
from .row import TableRow
from .style import TableStyle


@dataclass(kw_only=True)
class Table(Component):
    """Represent a table with externally prepared data."""

    columns: list[TableColumn] = field(default_factory=list)
    rows: Iterable[TableRow] = field(default_factory=list)
    header: str | None = None
    footer: TableRow | None = None
    table_style: TableStyle = field(default_factory=TableStyle)

    def __post_init__(self):
        """Validate table configuration without consuming data rows."""
        if not self.columns:
            raise ValueError("Table must contain at least one column.")
        if not all(isinstance(column, TableColumn) for column in self.columns):
            raise TypeError("All columns must be TableColumn instances.")
        keys = [column.key for column in self.columns]
        if len(keys) != len(set(keys)):
            raise ValueError("Table column keys must be unique.")
        if not isinstance(self.rows, Iterable):
            raise TypeError("Table rows must be iterable.")
        if self.footer is not None and not isinstance(self.footer, TableRow):
            raise TypeError("Table footer must be a TableRow.")
        if not isinstance(self.table_style, TableStyle):
            raise TypeError("Table style must be a TableStyle instance.")
