from ..renderers import DATA_RENDERERS
from ..values import cell_value
from ..worksheet import DataSheet


class DataEngine:
    """
    Write analysis-ready sheets: report information rows, then one typed sheet per table, append-only for streaming.
    """

    def __init__(self, workbook, context):
        """
        Prepare lazy sheet creation.
        """
        self.workbook, self.direction, self.options, self.information, self.tables, self.charts = workbook, context.direction, workbook.options, None, 0, 0

    def write(self, document, context):
        """
        Render the document.
        """
        self.render(document, context)

    def render(self, component, context):
        """
        Render one component.
        """
        DATA_RENDERERS.get(component).render(component, context, self)

    def information_sheet(self):
        """
        Return the sheet holding texts and key/value pairs, created on first use.
        """
        if self.information is None:
            self.information = DataSheet(self.workbook.create_sheet(self.options.sheet_name), self.direction)
        return self.information

    def table_sheet(self, table):
        """
        Create the sheet for one table, named after its caption.
        """
        self.tables += 1
        return DataSheet(self.workbook.create_sheet(table.header or f"Table {self.tables}"), self.direction)

    def chart_sheet(self, chart):
        """
        Create the sheet for one chart, named after its title.
        """
        self.charts += 1
        return DataSheet(self.workbook.create_sheet(chart.title or f"Chart {self.charts}"), self.direction)

    def value(self, value):
        """
        Convert a report value for Excel using the configured decimal policy.
        """
        return cell_value(value, self.options.decimal_policy)
