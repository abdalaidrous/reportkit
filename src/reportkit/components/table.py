from dataclasses import dataclass, field
from typing import Any
from ..core.component import Component


@dataclass
class Table(Component):
    """
    Represent a configurable report table.
    """

    columns: list[Any] = field(default_factory=list)
    rows: list[Any] = field(default_factory=list)
    header: Any = None
    footer: Any = None
