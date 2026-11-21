from datetime import date, datetime
from decimal import Decimal, InvalidOperation


class ValueFormatter:
    """
    Format values for report presentation.
    """

    @classmethod
    def format(
        cls,
        value,
        format_type=None,
        decimals=2,
        currency=None,
        date_format=None,
    ):
        """
        Format a value using its requested presentation type.
        """
        if value is None:
            return ""

        if format_type in {None, "text"}:
            return str(value)
        if format_type == "number":
            return cls.number(value, decimals)
        if format_type == "currency":
            return cls.currency(value, decimals, currency)
        if format_type == "percent":
            return cls.percent(value, decimals)
        if format_type == "date":
            return cls.date(value, date_format or "%Y-%m-%d")
        if format_type == "datetime":
            return cls.datetime(value, date_format or "%Y-%m-%d %H:%M")

        raise ValueError("Invalid format type.")

    @staticmethod
    def number(value, decimals=2):
        """
        Format a finite numeric value.
        """
        if isinstance(value, bool):
            raise ValueError("Boolean values cannot be formatted as numbers.")

        if (
            not isinstance(decimals, int)
            or isinstance(decimals, bool)
            or not 0 <= decimals <= 12
        ):
            raise ValueError("Decimals must be an integer between 0 and 12.")

        try:
            number = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Invalid numeric value.") from None

        if not number.is_finite():
            raise ValueError("Numeric values must be finite.")

        return f"{number:,.{decimals}f}"

    @classmethod
    def currency(cls, value, decimals=2, currency=None):
        """
        Format monetary values with an optional currency label.
        """
        formatted = cls.number(value, decimals)
        return f"{formatted} {currency}" if currency else formatted

    @classmethod
    def percent(cls, value, decimals=2):
        """
        Format fractional values as percentages.
        """
        try:
            number = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Invalid numeric value.") from None

        if not number.is_finite():
            raise ValueError("Percentage must be finite.")

        return f"{cls.number(number * 100, decimals)}%"

    @staticmethod
    def date(value, date_format="%Y-%m-%d"):
        """
        Format a date value.
        """
        if not isinstance(value, (date, datetime)):
            raise TypeError("Expected a date or datetime instance.")

        return value.strftime(date_format)

    @staticmethod
    def datetime(value, date_format="%Y-%m-%d %H:%M"):
        """
        Format a datetime value.
        """
        if not isinstance(value, datetime):
            raise TypeError("Expected a datetime instance.")

        return value.strftime(date_format)
