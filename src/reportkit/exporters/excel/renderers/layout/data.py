from .....components.information import KeyValue
from .....components.typography import Heading, RichText, Text
from .....styles.style import Style
from ...values import component_text

INLINE = (Text, Heading, RichText, KeyValue)


class StackDataRenderer:
    """
    Visit a container's children in the data mode.
    """

    def render(self, component, context, engine):
        """
        Render every child in order.
        """
        for child in component.children:
            engine.render(child, context)


class ColumnsDataRenderer:
    """
    Write side-by-side texts as one row in the data mode; other children are rendered one by one.
    """

    def render(self, component, context, engine):
        """
        Append inline children as the columns of one row, or render each child in order.
        """
        if component.children and all(isinstance(child, INLINE) for child in component.children):
            engine.information_sheet().append([(engine.value(component_text(child)), Style(), None) for child in component.children])
            return
        for child in component.children:
            engine.render(child, context)


class SkipDataRenderer:
    """
    Declare decorative components (spacing, rules, images, page settings) that carry no data in the data mode.
    """

    def render(self, component, context, engine):
        """
        Write nothing for a decorative component.
        """
