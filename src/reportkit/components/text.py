from dataclasses import dataclass
from ..core.component import Component


@dataclass
class Text(Component):
    """
    Represent a text component.
    """

    value: str = ""


@dataclass
class Heading(Component):
    """
    Represent a heading component.
    """

    value: str = ""
    level: int = 1
