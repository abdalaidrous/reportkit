from decimal import Decimal

from ..exceptions import ExcelExportError

EXCEL_DIGITS = 15
EXCEL_MAX_NUMBER = Decimal("9.99999999999999E+307")


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
