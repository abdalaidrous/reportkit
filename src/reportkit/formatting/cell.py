from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class FormattedTableCell:
    """
    Hold a plain value formatted for display; tone is 'positive', 'negative' or None.
    """

    display: str
    align: str = "start"
    tone: str | None = None
