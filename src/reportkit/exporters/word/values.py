from ...components.information import KeyValue
from ...components.table import TableCell
from ...components.typography import Heading, RichText, Text
from ...formatting.cells import TableCellFormatter
from .exceptions import WordExportError


def cell_text(content, column):
    """
    Resolve the display text of a table cell.
    """
    if isinstance(content, TableCell):
        return table_cell_text(content, column)

    return display(content, column)


def table_cell_text(content, column):
    """
    Resolve the text of an explicit table cell.
    """
    if content.children:
        return "\n".join(component_text(child) for child in content.children)

    return display(content.value, column)


def display(value, column):
    """
    Format a value using its column configuration.
    """
    if column is None:
        return "" if value is None else str(value)

    return TableCellFormatter.format(value, column).display


def component_text(component):
    """
    Resolve the text of a supported table cell component.
    """
    if isinstance(component, (Text, Heading)):
        return component.value

    if isinstance(component, RichText):
        return rich_text(component)

    if isinstance(component, KeyValue):
        return key_value_text(component)

    raise WordExportError(f"{type(component).__name__} cannot be shown inside a Word table cell.")


def rich_text(component):
    """
    Join the text of rich text spans.
    """
    return "".join(span.value for span in component.spans)


def key_value_text(component):
    """
    Format a key-value component as text.
    """
    value = "" if component.value is None else component.value
    return f"{component.label}: {value}"