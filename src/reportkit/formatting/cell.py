from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class FormattedTableCell:
    """
    Represent a formatted cell ready for rendering.
    """

    display: str
    align: str = "start"
    colspan: int = 1
    rowspan: int = 1
    style: str = ""
    color: str | None = None
