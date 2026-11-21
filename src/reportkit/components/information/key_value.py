from dataclasses import dataclass, field
from typing import Any

from ...core.component import Component
from ...styles.style import Style


@dataclass(kw_only=True)
class KeyValue(Component):
    """Represent a labeled value."""

    label: str
    value: Any = None
    secondary_label: str | None = None
    orientation: str = "horizontal"
    label_style: Style = field(default_factory=Style)
    value_style: Style = field(default_factory=Style)

    def __post_init__(self):
        """Validate the information field."""
        if not isinstance(self.label, str):
            raise TypeError("Label must be a string.")
        if self.orientation not in {"horizontal", "vertical"}:
            raise ValueError("Unsupported KeyValue orientation.")
