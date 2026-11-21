import math
from datetime import date, datetime
from decimal import Decimal

from ..exceptions import ExcelExportError
from .numbers import number_value

EXCEL_MAX_TEXT = 32767
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def cell_value(value, decimal_policy="error"):
    """
    Convert a prepared report value into a value Excel stores natively, without changing it.
    """
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        return text_value(value)
    if isinstance(value, (int, Decimal)):
        return number_value(Decimal(value), value, decimal_policy)
    if isinstance(value, float):
        return float_value(value)
    if isinstance(value, (date, datetime)):
        return date_value(value)
    raise ExcelExportError(f"Unsupported value type for Excel export: {type(value).__name__}.")


def float_value(value):
    """
    Accept finite floats only.
    """
    if not math.isfinite(value):
        raise ExcelExportError(f"Non-finite number cannot be written to Excel: {value}.")
    return value


def date_value(value):
    """
    Accept naive dates and datetimes; Excel has no time zones.
    """
    if isinstance(value, datetime) and value.tzinfo is not None:
        raise ExcelExportError(f"Excel cannot store time zones; convert {value} to a naive datetime first.")
    return value


def text_value(value):
    """
    Accept text within Excel's cell limit.
    """
    if len(value) > EXCEL_MAX_TEXT:
        raise ExcelExportError(f"Text longer than {EXCEL_MAX_TEXT} characters cannot be written to one Excel cell.")
    return value


def is_formula_like(value):
    """
    Return whether text would be read as a formula by Excel or spreadsheet tools.
    """
    return isinstance(value, str) and value.startswith(FORMULA_PREFIXES)
