from .....components.table import TableCell
from .....styles.style import Style
from ...values import component_text, number_format


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
