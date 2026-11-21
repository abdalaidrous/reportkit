from decimal import Decimal

from .cell import FormattedTableCell
from .values import ValueFormatter


class TableCellFormatter:
    """
    Format plain table values using their column rules.
    """

    @classmethod
    def format(cls, value, column):
        """
        Build the display text, alignment and numeric tone.
        """
        date_format = column.date_format or ("%Y-%m-%d %H:%M" if column.format == "datetime" else "%Y-%m-%d")
        display = ValueFormatter.format(value, format_type=column.format, decimals=column.decimals, currency=column.currency, date_format=date_format)
        return FormattedTableCell(display=display, align=column.align, tone=cls.resolve_tone(value, column))

    @staticmethod
    def resolve_tone(value, column):
        """
        Return 'negative' or 'positive' for signed numeric values.
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
            return "negative"
        if number > 0:
            return "positive"

        return None
