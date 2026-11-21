from dataclasses import dataclass

from ...core.component import Component


@dataclass
class Heading(Component):
    """Represent a heading component."""

    value: str = ""
    level: int = 1
