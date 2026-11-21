from openpyxl.styles import Border


def edge_borders(style):
    """
    Return the left, right, top and bottom borders of a component style.
    """
    whole = f"{style.border_width or 1}px {style.border_style or 'solid'} {style.border_color}" if style.border_color else None
    return [side or whole for side in (style.border_left, style.border_right, style.border_top, style.border_bottom)]


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
