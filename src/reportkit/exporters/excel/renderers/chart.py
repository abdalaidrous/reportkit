import math

from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.series import DataPoint
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.utils import get_column_letter

from ....rendering.chart import chart_colors
from ....styles.style import Style
from .media import ROW_HEIGHT_PIXELS

CENTIMETRES_PER_PIXEL = 2.54 / 96
CHART_TYPES = {"bar": BarChart, "line": LineChart, "pie": PieChart}


class ChartRenderer:
    """
    Render a Chart as a native Excel chart; its values go to a hidden data sheet, since Excel charts read cells.
    """

    def render(self, component, context, engine, region):
        """
        Write the chart values, anchor the chart centred in the region and return the rows it covers.
        """
        data = engine.chart_data()
        first_row = ChartData.write(data, component, engine)
        engine.sheet.add_chart(ChartData.chart(component, data.worksheet, first_row), region.row, region.column, region.width, component.width)
        return max(1, math.ceil(component.height / ROW_HEIGHT_PIXELS))


class ChartDataRenderer:
    """
    Render a Chart in the data mode: its own sheet with the values as a table, and the native chart beside them.
    """

    def render(self, component, context, engine):
        """
        Write the values from the first row and anchor the chart to their right.
        """
        sheet = engine.chart_sheet(component)
        ChartData.write(sheet, component, engine)
        sheet.worksheet.add_chart(ChartData.chart(component, sheet.worksheet, 1), f"{get_column_letter(len(component.series) + 3)}1")


class ChartData:
    """
    Write chart values as a block of cells (a header row, then one row per label) and build the chart reading them.
    """

    @staticmethod
    def write(sheet, component, engine):
        """
        Append the block and return its header row.
        """
        first_row = sheet.rows + 1
        number_format = values_format(component.decimals)
        sheet.append([(None, Style(), None)] + [(series.name, Style(font_weight=700), None) for series in component.series])
        for position, label in enumerate(component.labels):
            sheet.append([(engine.value(label), Style(), None)] + [(engine.value(series.values[position]), Style(), number_format) for series in component.series])
        return first_row

    @classmethod
    def chart(cls, component, worksheet, first_row):
        """
        Build the openpyxl chart over the block written at first_row.
        """
        chart = CHART_TYPES[component.chart_type]()
        last_row = first_row + len(component.labels)
        chart.add_data(Reference(worksheet, min_col=2, max_col=len(component.series) + 1, min_row=first_row, max_row=last_row), titles_from_data=True)
        chart.set_categories(Reference(worksheet, min_col=1, min_row=first_row + 1, max_row=last_row))
        chart.title = component.title or None
        chart.width, chart.height = component.width * CENTIMETRES_PER_PIXEL, component.height * CENTIMETRES_PER_PIXEL
        if not component.legend:
            chart.legend = None
        cls.paint(chart, component)
        cls.configure(chart, component)
        return chart

    @staticmethod
    def paint(chart, component):
        """
        Give the series (or the pie slices) the report chart colors.
        """
        colors = [color.lstrip("#") for color in chart_colors(component)]
        if component.chart_type == "pie":
            chart.series[0].data_points = [DataPoint(idx=index, spPr=GraphicalProperties(solidFill=color)) for index, color in enumerate(colors)]
            return
        for series, color in zip(chart.series, colors):
            if component.chart_type == "line":
                series.graphicalProperties.line.solidFill = color
                series.smooth = False
            else:
                series.graphicalProperties.solidFill = color

    @staticmethod
    def configure(chart, component):
        """
        Show the axes (openpyxl hides them by default), the value format and the optional value labels.
        """
        if component.chart_type != "pie":
            chart.x_axis.delete = chart.y_axis.delete = False
            chart.y_axis.number_format = values_format(component.decimals)
        if component.show_values:
            chart.dataLabels = DataLabelList()
            chart.dataLabels.showVal = component.chart_type != "pie"
            chart.dataLabels.showPercent = component.chart_type == "pie"



def values_format(decimals):
    """
    Return the Excel number format of chart values with the chart decimals.
    """
    return "#,##0." + "0" * decimals if decimals else "#,##0"
