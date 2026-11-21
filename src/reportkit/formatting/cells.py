from decimal import Decimal

from .cell import FormattedTableCell
from .values import ValueFormatter


class TableCellFormatter:
    """
    Prepare table cells using column formatting rules.
    """

    @classmethod
    def format(cls, value, column):
        """
        Build a formatted table cell.
        """
        display = ValueFormatter.format(
            value,
            format_type=column.format,
            decimals=column.decimals,
            currency=column.currency,
            date_format=column.date_format
            or ("%Y-%m-%d %H:%M" if column.format == "datetime" else "%Y-%m-%d"),
        )
        return FormattedTableCell(
            display=display,
            align=column.align,
            color=cls.resolve_color(value, column),
        )

    @staticmethod
    def resolve_color(value, column):
        """
        Resolve financial colors for numeric values.
        """
        if column.format not in {"number", "currency"} or value is None:
            return None

        try:
            number = Decimal(str(value))
        except (ValueError, TypeError, ArithmeticError):
            return None

        if not number.is_finite():
            return None
        if number < 0:
            return "#dc2626"
        if number > 0:
            return "#059669"

        return None
