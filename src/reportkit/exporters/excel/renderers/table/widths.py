from ..base import distribute, track_shares

MIN_COLUMN_CHARACTERS = 12


def get_widths(component, engine, region):
    """
    Share the region between the columns: declared widths first, the rest by header length like the HTML auto layout.
    """
    tracks = [column.width or f"{max(len(column.title), len(column.subtitle or ''), MIN_COLUMN_CHARACTERS)}fr" for column in component.columns]
    return distribute(track_shares(tracks, engine.sheet.content_pixels), region.width)


def spans(region, widths):
    """
    Return the first grid column and width of every table column.
    """
    return [(region.column + sum(widths[:index]), width) for index, width in enumerate(widths)]


def width_characters(column):
    """
    Convert a declared column width into Excel characters for data sheets, or estimate it from the header.
    """
    width = column.width or ""
    if width.endswith("%"):
        return round(float(width[:-1]) * 1.1, 1)
    if width.endswith("px"):
        return round(float(width[:-2]) / 7, 1)
    if width.endswith("mm"):
        return round(float(width[:-2]) * 0.55, 1)
    return min(40, max(10, len(column.title), len(column.subtitle or "")) + 4)
