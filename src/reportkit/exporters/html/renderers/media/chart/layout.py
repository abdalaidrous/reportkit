import math
from dataclasses import dataclass
from decimal import Decimal

from ......formatting.values import ValueFormatter
from ....direction import text_direction

TICKS = 5
LABEL_SIZE = 11
CHARACTER_WIDTH = 0.6  # Average glyph width as a share of the font size, to keep axis labels apart.
BAND_FILL = 0.7
LABEL_BOX = 160  # Width of the box a label is aligned in, wider than any axis label.
PIE_LABEL_MINIMUM = 0.04  # Slices smaller than this share keep their value in the legend only.


@dataclass(frozen=True)
class Bar:
    x: float
    y: float
    width: float
    height: float
    color: str


@dataclass(frozen=True)
class Label:
    x: float
    y: float
    text: str
    anchor: str = "middle"
    tone: str = "label"

    def box(self, width, height):
        """
        Place the label as an HTML box over the drawing, in percentages so it follows the drawing when it scales:
        SVG text is not shaped for Arabic by every renderer, HTML text is.
        """
        left = {"end": self.x - LABEL_BOX, "start": self.x}.get(self.anchor, self.x - LABEL_BOX / 2)
        return {
            "left": percent(left, width),
            "top": percent(self.y - LABEL_SIZE * 0.85, height),
            "width": percent(LABEL_BOX, width),
            "align": {"end": "right", "start": "left"}.get(self.anchor, "center"),
            "dir": text_direction(self.text) or "ltr",
            "text": self.text,
            "tone": self.tone,
        }


@dataclass(frozen=True)
class Line:
    points: str
    color: str
    dots: tuple


@dataclass(frozen=True)
class Slice:
    path: str
    color: str


def text_width(text, size=LABEL_SIZE):
    """
    Estimate the width of a label in pixels.
    """
    return len(text) * size * CHARACTER_WIDTH


class ValueScale:
    """
    Map values to vertical positions on a zero-based axis with round tick values.
    """

    def __init__(self, values, top, bottom, decimals):
        """
        Choose round ticks covering zero and every value.
        """
        low, high = min(0.0, *values), max(0.0, *values)
        high = high if high > low else low + 1
        self.step = nice_step((high - low) / TICKS)
        self.low = math.floor(low / self.step) * self.step
        self.high = math.ceil(high / self.step) * self.step
        self.top, self.bottom = top, bottom
        self.decimals = max(decimals, step_decimals(self.step))

    def position(self, value):
        """
        Return the vertical position of a value.
        """
        return self.bottom - (float(value) - self.low) / (self.high - self.low) * (self.bottom - self.top)

    def ticks(self):
        """
        Return (position, label) for every tick from the lowest to the highest.
        """
        count = round((self.high - self.low) / self.step)
        return [(self.position(self.low + index * self.step), ValueFormatter.number(round(self.low + index * self.step, 10), self.decimals)) for index in range(count + 1)]


class CartesianLayout:
    """
    Lay out a bar or line chart: value axis with grid lines, one band per label, bars or lines per series.
    """

    def __init__(self, chart, colors):
        """
        Compute the plot area from the label sizes, then every mark.
        """
        self.chart, self.colors = chart, colors
        values = [float(value) for series in chart.series for value in series.values]
        top = LABEL_SIZE * 2 if chart.show_values else LABEL_SIZE
        below = chart.show_values and min(values) < 0  # Room for the labels under negative values.
        bottom = chart.height - LABEL_SIZE * (3.6 if below else 2.4)
        self.scale = ValueScale(values, top, bottom, chart.decimals)
        ticks = self.scale.ticks()
        self.left = max(text_width(label) for _, label in ticks) + LABEL_SIZE
        self.right = chart.width - LABEL_SIZE
        self.band = (self.right - self.left) / len(chart.labels)
        self.ticks = [Label(self.left - LABEL_SIZE / 2, position + LABEL_SIZE * 0.35, label, "end") for position, label in ticks]
        self.grid = [position for position, _ in ticks]
        self.zero = self.scale.position(0)

    def center(self, position):
        """
        Return the horizontal center of a label's band.
        """
        return self.left + self.band * (position + 0.5)

    def categories(self):
        """
        Return the label under every band, skipping labels when they would overlap.
        """
        widest = max(text_width(label) for label in self.chart.labels)
        every = max(1, math.ceil((widest + LABEL_SIZE) / self.band))
        return [Label(self.center(position), self.chart.height - LABEL_SIZE * 0.8, label) for position, label in enumerate(self.chart.labels) if position % every == 0]

    def bars(self):
        """
        Return one bar per value, the series of a label side by side inside its band.
        """
        width = self.band * BAND_FILL / len(self.chart.series)
        bars = []
        for index, series in enumerate(self.chart.series):
            for position, value in enumerate(series.values):
                x = self.center(position) - self.band * BAND_FILL / 2 + index * width
                y = self.scale.position(value)
                bars.append(Bar(x, min(y, self.zero), width, abs(self.zero - y), self.colors[index]))
        return bars

    def lines(self):
        """
        Return one line per series through the band centers.
        """
        lines = []
        for index, series in enumerate(self.chart.series):
            dots = tuple((self.center(position), self.scale.position(value)) for position, value in enumerate(series.values))
            lines.append(Line(" ".join(f"{x:.2f},{y:.2f}" for x, y in dots), self.colors[index], dots))
        return lines

    def values(self):
        """
        Return the value labels above positive values and below negative ones.
        """
        if not self.chart.show_values:
            return []
        marks = self.bars() if self.chart.chart_type == "bar" else [Bar(x, y, 0, 0, "") for line in self.lines() for x, y in line.dots]
        values = [value for series in self.chart.series for value in series.values]
        return [self.value_label(mark, value) for mark, value in zip(marks, values)]

    def value_label(self, mark, value):
        """
        Place one value label at the outer end of its mark.
        """
        x = mark.x + mark.width / 2
        if value < 0:
            return Label(x, mark.y + mark.height + LABEL_SIZE * 1.1, self.format(value))
        return Label(x, mark.y - LABEL_SIZE * 0.4, self.format(value))

    def format(self, value):
        """
        Format a value with the chart decimals.
        """
        return ValueFormatter.number(value, self.chart.decimals)

    def labels(self):
        """
        Return every text of the chart: axis ticks, values and categories.
        """
        return self.ticks + self.values() + self.categories()


class PieLayout:
    """
    Lay out a pie chart: one slice per label, clockwise from the top.
    """

    def __init__(self, chart, colors):
        """
        Center the pie in the chart area.
        """
        self.chart, self.colors = chart, colors
        self.values = [Decimal(str(value)) for value in chart.series[0].values]
        self.total = sum(self.values)
        self.cx, self.cy = chart.width / 2, chart.height / 2
        self.radius = min(chart.width, chart.height) / 2 - LABEL_SIZE / 2

    def slices(self):
        """
        Return one path per non-empty slice; a single slice is a full circle.
        """
        slices, start = [], 0.0
        for value, color in zip(self.values, self.colors):
            share = float(value / self.total)
            if share >= 1:
                slices.append(Slice(self.circle(), color))
            elif share > 0:
                slices.append(Slice(self.arc(start, start + share), color))
            start += share
        return slices

    def labels(self):
        """
        Return the percentage of every slice large enough to hold it.
        """
        if not self.chart.show_values:
            return []
        labels, start = [], 0.0
        for value in self.values:
            share = float(value / self.total)
            if share >= PIE_LABEL_MINIMUM:
                x, y = self.point(start + share / 2, self.radius * 0.65)
                labels.append(Label(x, y + LABEL_SIZE * 0.35, ValueFormatter.number(share * 100, self.chart.decimals) + "%", tone="inverse"))
            start += share
        return labels

    def arc(self, start, end):
        """
        Return the path of the slice between two shares of the circle.
        """
        x1, y1 = self.point(start, self.radius)
        x2, y2 = self.point(end, self.radius)
        large = 1 if end - start > 0.5 else 0
        return f"M {self.cx:.2f} {self.cy:.2f} L {x1:.2f} {y1:.2f} A {self.radius:.2f} {self.radius:.2f} 0 {large} 1 {x2:.2f} {y2:.2f} Z"

    def circle(self):
        """
        Return the path of a full circle, drawn as two half arcs.
        """
        top, bottom = self.cy - self.radius, self.cy + self.radius
        return f"M {self.cx:.2f} {top:.2f} A {self.radius:.2f} {self.radius:.2f} 0 1 1 {self.cx:.2f} {bottom:.2f} A {self.radius:.2f} {self.radius:.2f} 0 1 1 {self.cx:.2f} {top:.2f} Z"

    def point(self, share, radius):
        """
        Return the point at a share of the circle, clockwise from the top.
        """
        angle = 2 * math.pi * share - math.pi / 2
        return self.cx + radius * math.cos(angle), self.cy + radius * math.sin(angle)


def percent(value, total):
    """
    Return a length as a CSS percentage of the drawing size.
    """
    return f"{value / total * 100:.3f}%"


def nice_step(raw):
    """
    Round a raw tick step up to 1, 2, 2.5 or 5 times a power of ten.
    """
    magnitude = 10 ** math.floor(math.log10(raw))
    return next(factor * magnitude for factor in (1, 2, 2.5, 5, 10) if factor * magnitude >= raw - 1e-12)


def step_decimals(step):
    """
    Return the decimals needed to write a tick step exactly.
    """
    exponent = Decimal(str(round(step, 10))).normalize().as_tuple().exponent
    return max(0, -exponent)
