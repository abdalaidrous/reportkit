from collections.abc import Iterable
from dataclasses import dataclass, field

from ...core.component import Component
from ...validators.table.table import TableValidator
from .column import TableColumn
from .row import TableRow
from .style import TableStyle


@dataclass(kw_only=True)
class Table(Component):
    """Define a table with externally prepared rows; rows may be a lazy iterable."""

    columns: list[TableColumn] = field(default_factory=list)
    rows: Iterable[TableRow] = field(default_factory=list)
    header: str | None = None
    footer: TableRow | None = None
    table_style: TableStyle = field(default_factory=TableStyle)

    def __post_init__(self):
        """Validate the table without consuming its rows."""
        TableValidator.validate(self)
