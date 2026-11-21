from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class TableStyle:
    """Define table-specific presentation settings."""

    bordered: bool = True
    striped: bool = False
    hover: bool = False
    compact: bool = False
    repeat_header: bool = True
    avoid_row_break: bool = True
    show_header: bool = True
    ruled: bool = False
    layout: str = "fixed"

    def __post_init__(self):
        """Validate the table layout mode."""
        if self.layout not in {"fixed", "auto"}:
            raise ValueError("Table layout must be 'fixed' or 'auto'.")
