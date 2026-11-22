from ....components.document import Page
from ....styles.borders import edge_borders
from ..renderers import FORMATTED_RENDERERS
from ..renderers.base import Region
from ..styles import pixels
from ..values import cell_value
from ..worksheet import GRID_COLUMNS, DataSheet, FormattedSheet

CHART_DATA_SHEET = "Chart data"


class FormattedEngine:
    """
    Lay the report out on one page-wide sheet like the HTML/PDF output, with margins, outlines and print settings.
    """

    def __init__(self, workbook, context, document):
        """
        Create the report sheet sized to the first page of the document.
        """
        page = next(find_components(document, Page), None)
        self.sheet, self.options = FormattedSheet(workbook.create_sheet(workbook.options.sheet_name), context.direction, page), workbook.options
        self.workbook, self.direction, self.chart_values = workbook, context.direction, None

    def write(self, document, context):
        """
        Render the document across the whole column grid.
        """
        self.render(document, context, Region(1, 1, GRID_COLUMNS))
        self.sheet.finish()

    def render(self, component, context, region):
        """
        Render one component with its vertical margins, outline and background, and return the rows it used.
        """
        style = context.resolve_style(component)
        top = self.add_gap(region.row, style.margin_top)
        height = FORMATTED_RENDERERS.get(component).render(component, context, self, region.below(top))
        if height and (style.background_color or edge_borders(style) != [None] * 4):
            self.sheet.outline(region.row + top, region.column, region.width, height, style)
        return top + height + self.add_gap(region.row + top + height, style.margin_bottom)

    def add_gap(self, row, margin):
        """
        Turn a vertical CSS margin into an empty row of the same height.
        """
        if not margin or pixels(margin) < 4:
            return 0
        self.sheet.set_row_height(row, pixels(margin) * 0.75)
        return 1

    def chart_data(self):
        """
        Return the hidden sheet that holds the values charts read, created on first use.
        """
        if self.chart_values is None:
            worksheet = self.workbook.create_sheet(CHART_DATA_SHEET)
            worksheet.sheet_state = "hidden"
            self.chart_values = DataSheet(worksheet, self.direction)
        return self.chart_values

    def value(self, value):
        """
        Convert a report value for Excel using the configured decimal policy.
        """
        return cell_value(value, self.options.decimal_policy)


def find_components(component, kind):
    """
    Yield the components of one type in the tree without touching table rows.
    """
    if isinstance(component, kind):
        yield component
    for child in getattr(component, "children", []):
        yield from find_components(child, kind)
