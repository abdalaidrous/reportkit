from dataclasses import dataclass

from ...core.container import Container


@dataclass(kw_only=True)
class Header(Container):
    """
    Represent a report header container.
    """

    repeat: bool = False
