from dataclasses import dataclass

from ...validators.table.column import TableColumnValidator


@dataclass(frozen=True, kw_only=True)
class TableColumn:
    """Define a table column and its presentation options."""

    key: str
    title: str
    subtitle: str | None = None
    width: str | None = None
    align: str = "start"
    header_align: str | None = None
    vertical_align: str = "middle"
    nowrap: bool = False
    format: str | None = None
    decimals: int = 2
    currency: str | None = None
    date_format: str | None = None

    def __post_init__(self):
        """Validate the column definition."""
        TableColumnValidator.validate(self)
