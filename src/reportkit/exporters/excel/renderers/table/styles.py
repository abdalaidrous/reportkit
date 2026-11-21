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
