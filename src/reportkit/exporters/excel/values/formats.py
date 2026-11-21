import re

from ..exceptions import ExcelExportError

DATE_TOKENS = {"%Y": "yyyy", "%y": "yy", "%m": "mm", "%d": "dd", "%H": "hh", "%I": "hh", "%M": "mm", "%S": "ss", "%p": "AM/PM", "%b": "mmm", "%B": "mmmm", "%a": "ddd", "%A": "dddd", "%%": "%"}


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
