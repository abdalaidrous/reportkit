from dataclasses import dataclass, field
from typing import Any

from ...styles.style import Style


@dataclass(frozen=True, kw_only=True)
class TableCell:
    """Represent one externally prepared table cell."""

    value: Any = None
    align: str = "start"
    colspan: int = 1
    rowspan: int = 1
    style: Style = field(default_factory=Style)

    def __post_init__(self):
        """Validate cell presentation options."""
        if self.align not in {"start", "center", "end", "left", "right"}:
            raise ValueError("Invalid cell alignment.")
        for name, span in (("colspan", self.colspan), ("rowspan", self.rowspan)):
            if not isinstance(span, int) or isinstance(span, bool) or span < 1:
                raise ValueError(f"Table cell {name} must be a positive integer.")
