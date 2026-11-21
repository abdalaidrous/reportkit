from dataclasses import dataclass, field
from typing import Any

from ...core.component import Component
from ...styles.style import Style
from ...validators.table.cell import TableCellValidator


@dataclass(frozen=True, kw_only=True)
class TableCell:
    """Define one prepared cell: a plain value or a stack of child components; align=None inherits the column."""

    value: Any = None
    children: list[Component] = field(default_factory=list)
    align: str | None = None
    colspan: int = 1
    rowspan: int = 1
    style: Style = field(default_factory=Style)

    def __post_init__(self):
        """Validate the cell definition."""
        TableCellValidator.validate(self)
