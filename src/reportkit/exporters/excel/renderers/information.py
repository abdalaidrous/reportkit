from ....styles.style import Style
from ..styles import token


class KeyValueRenderer:
    """
    Render a label and its value: side by side for horizontal, stacked for vertical.
    """

    def render(self, component, context, engine, region):
        """
        Write the label and value cells and return the rows used.
        """
        value, label_style, value_style = engine.value(component.value), self.get_label_style(component, context), self.get_value_style(component, context)
        if component.orientation == "vertical" or region.width == 1:
            engine.sheet.place(region.row, region.column, region.width, self.get_label(component), label_style)
            engine.sheet.place(region.row + 1, region.column, region.width, value, value_style)
            return 2
        label, cell = region.split([1, 1])
        engine.sheet.place(label.row, label.column, label.width, self.get_label(component), label_style)
        engine.sheet.place(cell.row, cell.column, cell.width, value, value_style)
        return 1

    @staticmethod
    def get_label(component):
        """
        Join the label and its secondary label.
        """
        return f"{component.label} / {component.secondary_label}" if component.secondary_label else component.label

    @staticmethod
    def get_label_style(component, context):
        """
        Use a muted label style under the component and label styles.
        """
        return Style(color=token("--rk-color-muted")).merge(context.resolve_style(component)).merge(component.label_style)

    @staticmethod
    def get_value_style(component, context):
        """
        Use a bold value style under the component and value styles.
        """
        return Style(font_weight=600).merge(context.resolve_style(component)).merge(component.value_style)


class KeyValueDataRenderer:
    """
    Write a label and its value as one row on the report information sheet.
    """

    def render(self, component, context, engine):
        """
        Append the label and the value with its original type.
        """
        engine.information_sheet().append([(KeyValueRenderer.get_label(component), Style(font_weight=700), None), (engine.value(component.value), Style(), None)])
