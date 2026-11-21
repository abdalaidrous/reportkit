from dataclasses import dataclass, field
from typing import Any

from ...core.component import Component
from ...styles.style import Style


@dataclass(frozen=True, kw_only=True)
class TableCell:
    """
    Represent one externally prepared table cell.
    """

    value: Any = None
    children: list[Component] = field(default_factory=list)
    align: str | None = None
    colspan: int = 1
    rowspan: int = 1
    style: Style = field(default_factory=Style)

    def __post_init__(self):
        """Validate cell presentation options."""
        if self.align not in {None, "start", "center", "end", "left", "right"}:
            raise ValueError("Invalid cell alignment.")

        if not isinstance(self.children, (list, tuple)) or not all(isinstance(child, Component) for child in self.children):
            raise TypeError("Table cell children must be Component instances.")

        for name, span in (("colspan", self.colspan), ("rowspan", self.rowspan)):
            if not isinstance(span, int) or isinstance(span, bool) or span < 1:
                raise ValueError(f"Table cell {name} must be a positive integer.")