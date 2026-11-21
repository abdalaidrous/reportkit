from ..exceptions import ExcelExportError
from .constants import PAPER_MILLIMETRES, PIXELS_PER_MILLIMETRE


def content_width(page):
    """
    Return the printable width of a page in pixels (A4 portrait with 15 mm margins when there is no Page).
    """
    if page is None:
        return (210 - 30) * PIXELS_PER_MILLIMETRE
    width, height = PAPER_MILLIMETRES.get(page.size, (210, 297))
    paper = height if page.orientation == "landscape" else width
    return (paper - millimetres(page.margin_left) - millimetres(page.margin_right)) * PIXELS_PER_MILLIMETRE


def millimetres(value):
    """
    Convert a CSS length such as "12mm" to millimetres.
    """
    factor = {"mm": 1, "cm": 10, "in": 25.4, "pt": 25.4 / 72}.get(str(value)[-2:])
    if factor is None:
        raise ExcelExportError(f"Page margin {value!r} must use mm, cm, in or pt.")
    return float(value[:-2]) * factor
