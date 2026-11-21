from dataclasses import dataclass

from ...core.container import Container


@dataclass(kw_only=True)
class Footer(Container):
    """
    Represent a report footer container.
    """

    repeat: bool = False
