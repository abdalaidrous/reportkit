from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal

from ...core.component import Component
from ...validators.media.chart import ChartValidator


@dataclass(kw_only=True)
class ChartSeries:
    """
    One named row of prepared values, one value per chart label.
    """

    name: str
    values: list[int | float | Decimal] = field(default_factory=list)
    color: str | None = None


@dataclass(kw_only=True)
class Chart(Component):
    """
    Represent a bar, line or pie chart of prepared values; ReportKit draws them and never computes them.
    """

    labels: list[str] = field(default_factory=list)
    series: list[ChartSeries] = field(default_factory=list)
    chart_type: str = "bar"
    title: str | None = None
    width: int = 640
    height: int = 280
    decimals: int = 0
    legend: bool = True
    show_values: bool = False

    def __post_init__(self):
        """
        Accept series given as mappings (as from a dictionary definition), then validate the chart.
        """
        self.series = [ChartSeries(**series) if isinstance(series, Mapping) else series for series in self.series]
        ChartValidator.validate(self)
