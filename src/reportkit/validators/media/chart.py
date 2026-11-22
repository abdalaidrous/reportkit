import math
import re
from decimal import Decimal

CHART_TYPES = {"bar", "line", "pie"}
COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


class ChartValidator:
    """
    Validate Chart definitions: every series has one finite value per label.
    """

    @classmethod
    def validate(cls, chart):
        """
        Run every chart rule.
        """
        cls.validate_type(chart)
        cls.validate_labels(chart.labels)
        cls.validate_series(chart)
        cls.validate_presentation(chart)

    @staticmethod
    def validate_type(chart):
        """
        The chart type is bar, line or pie.
        """
        if chart.chart_type not in CHART_TYPES:
            raise ValueError("Chart type must be 'bar', 'line' or 'pie'.")

    @staticmethod
    def validate_labels(labels):
        """
        Labels are a non-empty list of strings.
        """
        if not isinstance(labels, list) or not labels:
            raise ValueError("Chart labels must be a non-empty list.")
        if not all(isinstance(label, str) for label in labels):
            raise TypeError("Chart labels must be strings.")

    @classmethod
    def validate_series(cls, chart):
        """
        Validate every series; a pie shows one series of non-negative values that are not all zero.
        """
        from ...components.media.chart import ChartSeries  # Deferred: avoids a components/validators cycle.

        if not isinstance(chart.series, list) or not chart.series:
            raise ValueError("Chart must contain at least one series.")
        if not all(isinstance(series, ChartSeries) for series in chart.series):
            raise TypeError("All chart series must be ChartSeries instances.")
        for series in chart.series:
            cls.validate_one_series(series, len(chart.labels))
        if chart.chart_type == "pie":
            cls.validate_pie(chart.series)

    @staticmethod
    def validate_one_series(series, count):
        """
        A series has a name, one finite number per label and an optional hex color.
        """
        if not isinstance(series.name, str):
            raise TypeError("Chart series name must be a string.")
        if not isinstance(series.values, list) or len(series.values) != count:
            raise ValueError(f"Chart series '{series.name}' must have one value per label ({count}).")
        if not all(is_number(value) for value in series.values):
            raise ValueError(f"Chart series '{series.name}' values must be finite numbers.")
        if series.color is not None and (not isinstance(series.color, str) or not COLOR.fullmatch(series.color)):
            raise ValueError(f"Chart series '{series.name}' color must be a hex color such as '#2563eb'.")

    @staticmethod
    def validate_pie(series):
        """
        A pie divides one whole: one series, no negative slice, not all zero.
        """
        if len(series) != 1:
            raise ValueError("A pie chart shows exactly one series.")
        if any(value < 0 for value in series[0].values) or not any(series[0].values):
            raise ValueError("Pie chart values must be non-negative and not all zero.")

    @staticmethod
    def validate_presentation(chart):
        """
        Validate the size in pixels, decimals, title and flags.
        """
        for name in ("width", "height"):
            value = getattr(chart, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 80:
                raise ValueError(f"Chart {name} must be an integer of at least 80 pixels.")
        if not isinstance(chart.decimals, int) or isinstance(chart.decimals, bool) or not 0 <= chart.decimals <= 6:
            raise ValueError("Chart decimals must be an integer between 0 and 6.")
        if chart.title is not None and not isinstance(chart.title, str):
            raise TypeError("Chart title must be a string.")
        if not isinstance(chart.legend, bool) or not isinstance(chart.show_values, bool):
            raise TypeError("Chart legend and show_values must be booleans.")


def is_number(value):
    """
    Return whether the value is a finite int, float or Decimal (bool excluded).
    """
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        return False
    return value.is_finite() if isinstance(value, Decimal) else math.isfinite(value)
