from ...components.information import KeyValue
from ...components.table import TableCell
from ...components.typography import Heading, RichText, Text
from ...formatting.cells import TableCellFormatter
from .exceptions import WordExportError


def cell_text(content, column):
    """
    Return the display text of a table entry, formatted by its column like the HTML output.
    """
    if isinstance(content, TableCell):
        return "\n".join(component_text(child) for child in content.children) if content.children else display(content.value, column)
    return display(content, column)


def display(value, column):
    """
    Format a plain value with the column rules, or as text for explicit cells.
    """
    if column is None:
        return "" if value is None else str(value)
    return TableCellFormatter.format(value, column).display


def component_text(component):
    """
    Return the text of a component placed inside a table cell.
    """
    if isinstance(component, (Text, Heading)):
        return component.value
    if isinstance(component, RichText):
        return "".join(span.value for span in component.spans)
    if isinstance(component, KeyValue):
        return f"{component.label}: {'' if component.value is None else component.value}"
    raise WordExportError(f"{type(component).__name__} cannot be shown inside a Word table cell.")
