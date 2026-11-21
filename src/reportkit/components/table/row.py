from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from ...styles.style import Style
from .cell import TableCell


@dataclass(frozen=True, kw_only=True)
class TableRow:
    """Represent one externally prepared table row."""

    values: Mapping[str, Any] = field(default_factory=dict)
    kind: str = "data"
    cells: list[TableCell] | None = None
    style: Style = field(default_factory=Style)

    def __post_init__(self):
        """Validate the row presentation."""
        if self.kind not in {"data", "group-header", "subtotal", "total"}:
            raise ValueError("Unsupported table row kind.")
        if not isinstance(self.values, Mapping):
            raise TypeError("Table row values must be a mapping.")
        if self.cells is not None and not all(isinstance(cell, TableCell) for cell in self.cells):
            raise TypeError("Row cells must contain TableCell instances.")
