from ....components.information import KeyValue
from ....components.typography import Heading, RichText, Text
from ..exceptions import ExcelExportError


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
    raise ExcelExportError(f"{type(component).__name__} cannot be shown inside an Excel table cell.")
