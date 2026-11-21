from dataclasses import dataclass

from ...core.container import Container


@dataclass
class Grid(Container):
    """Arrange child components in a grid."""

    columns: int = 1
