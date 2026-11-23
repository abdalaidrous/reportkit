from .style import Style
from .tokens import token


def table_styles(base=Style()):
    """
    Build the table styles from the shared table tokens, on top of the table component style.
    """
    divider, frame, ruled = f"1px solid {token('--rk-table-divider-color')}", f"1px solid {token('--rk-table-frame-color')}", token("--rk-table-ruled-color")
    return {
        "cell": base.merge(Style(color=token("--rk-table-cell-color"), border_bottom=divider)),
        "bordered": Style(border_left=divider, border_right=divider, border_top=divider, border_bottom=divider),
        "header": base.merge(Style(background_color=token("--rk-table-header-bg"), color=token("--rk-table-header-color"), font_weight=700, border_top=f"1px solid {token('--rk-table-header-accent')}", border_bottom=f"2px solid {token('--rk-table-header-rule')}")),
        "ruled": Style(border_top=f"1px solid {ruled}", border_bottom=f"2px solid {ruled}"),
        "frame": Style(border_left=frame, border_right=frame, border_top=frame, border_bottom=frame),
        "stripe": Style(background_color=token("--rk-table-stripe-bg")),
        "total": Style(background_color=token("--rk-table-total-bg"), font_weight=700, border_top=f"2px solid {token('--rk-table-divider-color')}"),
        "ruled-total": Style(font_weight=700, color=token("--rk-table-header-color"), border_top=f"2px solid {ruled}", border_bottom="0px none #ffffff"),
        "subtotal": Style(background_color=token("--rk-table-subtotal-bg"), font_weight=600),
        "group-header": Style(background_color=token("--rk-table-group-bg"), font_weight=700),
        "data": Style(),
        "compact": Style(font_size=token("--rk-font-xs")),
    }


def get_header_style(component, styles):
    """
    Combine the header, ruled and the table's own header styles.
    """
    table_style = component.table_style
    style = styles["header"].merge(styles["ruled"]) if table_style.ruled else styles["header"]
    return style.merge(table_style.header_style) if table_style.header_style is not None else style


def get_row_style(component, table_row, index, styles):
    """
    Combine the table, striping, row kind and row styles from the shared table styles.
    """
    table_style = component.table_style
    style = styles["cell"].merge(styles["bordered"]) if table_style.bordered else styles["cell"]
    if table_style.striped and table_row.kind == "data" and index % 2:
        style = style.merge(styles["stripe"])
    if table_style.compact:
        style = style.merge(styles["compact"])
    kind = "ruled-total" if table_style.ruled and table_row.kind == "total" else table_row.kind
    return style.merge(styles[kind]).merge(table_row.style)
