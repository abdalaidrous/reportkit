from ....rendering.chart import ChartTable
from .table import TableRenderer


class ChartRenderer:
    """
    Render a Chart as the table of its values: python-docx cannot draw charts, and the values stay readable and
    editable in Word.
    """

    def render(self, component, context, engine, area):
        """
        Render the chart values as a report table captioned with the chart title.
        """
        TableRenderer().render(ChartTable.build(component), context, engine, area)
