def edge_borders(style):
    """
    Return the left, right, top and bottom borders of a component style.
    """
    whole = f"{style.border_width or 1}px {style.border_style or 'solid'} {style.border_color}" if style.border_color else None
    return [side or whole for side in (style.border_left, style.border_right, style.border_top, style.border_bottom)]
