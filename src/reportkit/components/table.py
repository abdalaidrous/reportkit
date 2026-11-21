from dataclasses import dataclass, field
from typing import Any, Iterable
from ..core.component import Component


@dataclass(frozen=True, kw_only=True)
class TableColumn:
    """
    Define one table column and its presentation options.
    """

    key: str
    title: str
    width: str | None = None
    align: str = "start"
    format: str | None = None
    decimals: int = 2
    currency: str | None = None
    date_format: str | None = None

    def __post_init__(self):
        """
        Validate the column definition.
        """
        if not isinstance(self.key, str) or not self.key:
            raise ValueError("Column key must be a non-empty string.")

        if not isinstance(self.title, str):
            raise TypeError("Column title must be a string.")

        if self.align not in {"start", "center", "end", "left", "right"}:
            raise ValueError("Invalid column alignment.")

        if self.format not in {
            None,
            "text",
            "number",
            "currency",
            "percent",
            "date",
            "datetime",
        }:
            raise ValueError("Invalid column format.")

        if (
            not isinstance(self.decimals, int)
            or isinstance(self.decimals, bool)
            or not 0 <= self.decimals <= 12
        ):
            raise ValueError("Decimals must be an integer between 0 and 12.")


@dataclass(kw_only=True)
class Table(Component):
    """
    Represent a data table with defined columns and rows.
    """

    columns: list[TableColumn] = field(default_factory=list)
    rows: Iterable[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """
        Validate table columns without consuming data rows.
        """
        if not self.columns:
            raise ValueError("Table must contain at least one column.")

        if not all(isinstance(column, TableColumn) for column in self.columns):
            raise TypeError("All columns must be TableColumn instances.")

        keys = [column.key for column in self.columns]
        if len(keys) != len(set(keys)):
            raise ValueError("Table column keys must be unique.")

        if not isinstance(self.rows, Iterable):
            raise TypeError("Table rows must be iterable.")
