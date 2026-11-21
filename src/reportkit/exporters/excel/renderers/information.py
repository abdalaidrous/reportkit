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
            return self.render_stacked(component, engine, region, value, label_style, value_style)
        engine.sheet.write(region.row, region.column, self.get_label(component), label_style)
        engine.sheet.write(region.row, region.column + 1, value, value_style)
        engine.sheet.merge(region.row, region.column + 1, region.width - 1)
        return 1

    def render_stacked(self, component, engine, region, value, label_style, value_style):
        """
        Write the label above the value, each across the region.
        """
        engine.sheet.write(region.row, region.column, self.get_label(component), label_style)
        engine.sheet.write(region.row + 1, region.column, value, value_style)
        engine.sheet.merge(region.row, region.column, region.width)
        engine.sheet.merge(region.row + 1, region.column, region.width)
        return 2

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
