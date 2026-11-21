from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from ...styles.style import Style
from ...validators.table.row import TableRowValidator
from .cell import TableCell


@dataclass(frozen=True, kw_only=True)
class TableRow:
    """
    Define one prepared row; values may hold plain values or TableCell instances.
    """

    values: Mapping[str, Any] = field(default_factory=dict)
    kind: str = "data"
    cells: list[TableCell] | None = None
    style: Style = field(default_factory=Style)

    def __post_init__(self):
        """
        Validate the row definition.
        """
        TableRowValidator.validate(self)
