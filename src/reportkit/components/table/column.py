from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class TableColumn:
    """Define a table column and its presentation options."""

    key: str
    title: str
    width: str | None = None
    align: str = "start"
    format: str | None = None
    decimals: int = 2
    currency: str | None = None
    date_format: str | None = None
    header_align: str | None = None
    vertical_align: str = "middle"

    def __post_init__(self):
        """Validate the column definition."""
        if not isinstance(self.key, str) or not self.key:
            raise ValueError("Column key must be a non-empty string.")
        if not isinstance(self.title, str):
            raise TypeError("Column title must be a string.")
        if self.align not in {"start", "center", "end", "left", "right"}:
            raise ValueError("Invalid column alignment.")
        if self.header_align not in {None, "start", "center", "end", "left", "right"}:
            raise ValueError("Invalid column header alignment.")
        if self.vertical_align not in {"top", "middle", "bottom"}:
            raise ValueError("Invalid column vertical alignment.")
        if self.format not in {None, "text", "number", "currency", "percent", "date", "datetime"}:
            raise ValueError("Invalid column format.")
        if not isinstance(self.decimals, int) or isinstance(self.decimals, bool) or not 0 <= self.decimals <= 12:
            raise ValueError("Decimals must be an integer between 0 and 12.")
