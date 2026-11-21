from .....components.table import TableCell
from .....styles.style import Style
from ...values import component_text, number_format


def get_entries(component, table_row):
    """
    Pair each value or explicit cell with its column definition (None for explicit cells).
    """
    if table_row.cells is not None:
        return [(cell, None) for cell in table_row.cells]
    return [(table_row.values.get(column.key), column) for column in component.columns]


def prepare_entry(entry, engine):
    """
    Return the Excel value, cell style and number format of one entry.
    """
    content, column = entry
    align = Style(text_align=column.align) if column else Style()
    if not isinstance(content, TableCell):
        return engine.value(content), align, number_format(column)
    cell_align = Style(text_align=content.align) if content.align else align
    if content.children:
        return "\n".join(component_text(child) for child in content.children), cell_align.merge(content.style), None
    return engine.value(content.value), cell_align.merge(content.style), number_format(column)


def header_text(column, separator):
    """
    Join a column title and subtitle.
    """
    return f"{column.title}{separator}{column.subtitle}" if column.subtitle else column.title
