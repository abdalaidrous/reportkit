from dataclasses import dataclass

from ...core.container import Container


@dataclass(kw_only=True)
class InfoGrid(Container):
    """Arrange information components in a grid."""

    columns: int = 2
    gap: int = 12

    def __post_init__(self):
        """Validate the grid configuration."""
        super().__post_init__()
        if isinstance(self.columns, bool) or not isinstance(self.columns, int) or self.columns < 1:
            raise ValueError("Columns must be a positive integer.")
        if isinstance(self.gap, bool) or not isinstance(self.gap, int) or self.gap < 0:
            raise ValueError("Gap must be a non-negative integer.")
