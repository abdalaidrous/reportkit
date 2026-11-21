from copy import copy

from ..exceptions import ExcelExportError
from ..styles import get_format
from ..values import is_formula_like
from . import constants


def write_value(cell, value, style, direction, styles, number_format=None):
    """
    Write a value with its format; text is always stored as text so it can never run as a formula.
    """
    cell.value = value
    if isinstance(value, str):
        cell.data_type = "s"
    apply_style(cell, style, direction, styles, number_format or cell.number_format, is_formula_like(value))


def apply_style(cell, style, direction, styles, number_format=None, quote_prefix=False):
    """
    Give a cell its format, reusing the workbook style ids built for the same format; assigning openpyxl style objects
    hashes them every time, which dominates large exports.
    """
    key = (style, direction, number_format, quote_prefix)
    if key in styles:
        cell._style = copy(styles[key])
        return
    get_format(style, direction).apply(cell)
    cell.number_format, cell.quotePrefix = number_format or "General", quote_prefix
    styles[key] = copy(cell._style)


def check_limits(row, column):
    """
    Refuse positions outside the Excel grid (below 1 or beyond its limits) instead of writing a truncated sheet.
    """
    if not (1 <= row <= constants.MAX_ROWS and 1 <= column <= constants.MAX_COLUMNS):
        raise ExcelExportError(f"Excel worksheets hold rows 1 to {constants.MAX_ROWS:,} and columns 1 to {constants.MAX_COLUMNS:,}, so they are limited; the report needs row {row:,}, column {column:,}.")
