from functools import cache

from openpyxl.styles import Border

from ....styles.style import Style


def edge_borders(style):
    """
    Return the left, right, top and bottom borders of a component style.
    """
    whole = f"{style.border_width or 1}px {style.border_style or 'solid'} {style.border_color}" if style.border_color else None
    return [side or whole for side in (style.border_left, style.border_right, style.border_top, style.border_bottom)]


@cache
def edge_style(style, on_left, on_right, on_top, on_bottom):
    """
    Return the border-only style of a covered cell in a merged block (the block sides on the cell's edges), or None.
    """
    left, right, top, bottom = edge_borders(style)
    sides = {"border_left": left if on_left else None, "border_right": right if on_right else None, "border_top": top if on_top else None, "border_bottom": bottom if on_bottom else None}
    return Style(**sides) if any(sides.values()) else None


def edge_border(cell, sides, row, column, width, height):
    """
    Combine a cell's own border with the outline sides that fall on the block edges.
    """
    left, right, top, bottom = sides
    current = cell.border
    return Border(
        left=left if cell.column == column and left.style else current.left,
        right=right if cell.column == column + width - 1 and right.style else current.right,
        top=top if cell.row == row and top.style else current.top,
        bottom=bottom if cell.row == row + height - 1 and bottom.style else current.bottom,
    )
