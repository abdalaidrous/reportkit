from dataclasses import dataclass

from ...core.component import Component


@dataclass
class Spacer(Component):
    """
    Represent empty space between components.
    """

    height: float = 0
