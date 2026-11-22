from ..components.table import Table, TableColumn, TableRow
from ..styles.tokens import token

PALETTE = tuple(f"--rk-chart-{index}" for index in range(1, 7))


def chart_colors(chart):
    """
    Return one hex color per legend entry: per label for a pie, per series otherwise (a series color wins).
    """
    if chart.chart_type == "pie":
        return [token(PALETTE[index % len(PALETTE)]) for index in range(len(chart.labels))]
    return [series.color or token(PALETTE[index % len(PALETTE)]) for index, series in enumerate(chart.series)]


def legend_names(chart):
    """
    Return the legend entries in color order: the labels of a pie, the series names otherwise.
    """
    return list(chart.labels) if chart.chart_type == "pie" else [series.name for series in chart.series]


class ChartTable:
    """
    Turn a chart into a table of its values, for exporters that cannot draw charts: one row per label, one column per
    series.
    """

    LABEL_KEY = "label"

    @classmethod
    def build(cls, chart):
        """
        Build the table; the values are written as given, formatted with the chart decimals.
        """
        columns = [TableColumn(key=cls.LABEL_KEY, title="")] + [TableColumn(key=cls.key(index), title=series.name, align="end", format="number", decimals=chart.decimals) for index, series in enumerate(chart.series)]
        rows = [TableRow(values={cls.LABEL_KEY: label, **{cls.key(index): series.values[position] for index, series in enumerate(chart.series)}}) for position, label in enumerate(chart.labels)]
        return Table(columns=columns, rows=rows, header=chart.title)

    @staticmethod
    def key(index):
        """
        Return the column key of a series.
        """
        return f"series_{index}"
