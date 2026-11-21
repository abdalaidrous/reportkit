from dataclasses import dataclass

from ...core.container import Container


@dataclass
class Row(Container):
    """Arrange child components horizontally."""
