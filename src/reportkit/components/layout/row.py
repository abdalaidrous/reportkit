from dataclasses import dataclass

from ...core.container import Container


@dataclass
class Row(Container):
    """
    Arrange child components horizontally.
    """

    justify: str | None = None
    align: str | None = None
    gap: str | None = None
    wrap: bool = False
