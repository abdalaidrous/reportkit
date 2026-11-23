from dataclasses import dataclass

from ...styles.style import Style


@dataclass(frozen=True, kw_only=True)
class TableStyle:
    """
    Define table presentation and print settings.
    """

    bordered: bool = True
    striped: bool = False
    hover: bool = False
    compact: bool = False
    ruled: bool = False
    layout: str = "fixed"
    show_header: bool = True
    repeat_header: bool = True
    avoid_row_break: bool = True
    header_style: Style | None = None  # Merged over the header cells (for example a brand background and text color).
