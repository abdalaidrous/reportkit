import math
import re
from datetime import date, datetime
from decimal import Decimal

from ...components.information import KeyValue
from ...components.typography import Heading, RichText, Text
from .exceptions import ExcelExportError

EXCEL_DIGITS = 15
EXCEL_MAX_NUMBER = Decimal("9.99999999999999E+307")
EXCEL_MAX_TEXT = 32767
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")
DATE_TOKENS = {"%Y": "yyyy", "%y": "yy", "%m": "mm", "%d": "dd", "%H": "hh", "%I": "hh", "%M": "mm", "%S": "ss", "%p": "AM/PM", "%b": "mmm", "%B": "mmmm", "%a": "ddd", "%A": "dddd", "%%": "%"}


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


def number_value(number, original, decimal_policy):
    """
    Keep numbers Excel can store exactly (15 significant digits); otherwise follow the explicit decimal policy.
    """
    if not number.is_finite():
        raise ExcelExportError(f"Non-finite number cannot be written to Excel: {original}.")
    if len(number.normalize().as_tuple().digits) <= EXCEL_DIGITS and abs(number) <= EXCEL_MAX_NUMBER:
        return original if isinstance(original, int) else float(number)
    if decimal_policy == "text":
        return str(original)
    raise ExcelExportError(f"{original} has more than {EXCEL_DIGITS} significant digits, which Excel cannot store exactly; pass decimal_policy='text' to write it as text.")


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


def number_format(column):
    """
    Map a TableColumn format to an Excel number format, or None for plain text.
    """
    if column is None or column.format in (None, "text"):
        return None
    decimals = "0." + "0" * column.decimals if column.decimals else "0"
    if column.format == "number":
        return f"#,##{decimals}"
    if column.format == "currency":
        return f'#,##{decimals} "{column.currency}"' if column.currency else f"#,##{decimals}"
    if column.format == "percent":
        return f"{decimals}%"
    return date_format(column.date_format or ("%Y-%m-%d %H:%M" if column.format == "datetime" else "%Y-%m-%d"))


def date_format(pattern):
    """
    Translate a strftime pattern into an Excel date format.
    """
    unknown = set(re.findall(r"%.", pattern)) - DATE_TOKENS.keys()
    if unknown:
        raise ExcelExportError(f"Date format directives {sorted(unknown)} have no Excel equivalent.")
    return re.sub(r"%.", lambda match: DATE_TOKENS[match.group()], pattern)


def component_text(component):
    """
    Return the text of a component placed inside a table cell.
    """
    if isinstance(component, (Text, Heading)):
        return component.value
    if isinstance(component, RichText):
        return "".join(span.value for span in component.spans)
    if isinstance(component, KeyValue):
        return f"{component.label}: {'' if component.value is None else component.value}"
    raise ExcelExportError(f"{type(component).__name__} cannot be shown inside an Excel table cell.")
