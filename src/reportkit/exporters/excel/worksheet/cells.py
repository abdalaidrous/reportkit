from ..exceptions import ExcelExportError
from ..styles import get_format
from ..values import is_formula_like
from . import constants


def write_value(cell, value, style, direction, number_format=None):
    """
    Write a value with its format; text is always stored as text so it can never run as a formula.
    """
    cell.value = value
    if isinstance(value, str):
        cell.data_type = "s"
        cell.quotePrefix = is_formula_like(value)
    get_format(style, direction).apply(cell)
    if number_format:
        cell.number_format = number_format


def check_limits(row, column):
    """
    Refuse positions outside the Excel grid (below 1 or beyond its limits) instead of writing a truncated sheet.
    """
    if not (1 <= row <= constants.MAX_ROWS and 1 <= column <= constants.MAX_COLUMNS):
        raise ExcelExportError(f"Excel worksheets hold rows 1 to {constants.MAX_ROWS:,} and columns 1 to {constants.MAX_COLUMNS:,}, so they are limited; the report needs row {row:,}, column {column:,}.")
