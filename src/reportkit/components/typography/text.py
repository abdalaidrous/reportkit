from dataclasses import dataclass

from ...core.component import Component


@dataclass
class Text(Component):
    """Represent a text component."""

    value: str = ""
