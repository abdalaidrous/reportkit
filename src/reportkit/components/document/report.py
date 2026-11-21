from dataclasses import dataclass

from ...core.container import Container


@dataclass
class Report(Container):
    """
    Represent the root report document.
    """

    title: str = ""
