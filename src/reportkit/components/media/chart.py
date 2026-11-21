from dataclasses import dataclass
from typing import Any

from ...core.component import Component


@dataclass
class Chart(Component):
    """
    Represent a chart component.
    """

    data: Any = None
    chart_type: str = "bar"
