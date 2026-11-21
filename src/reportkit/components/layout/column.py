from dataclasses import dataclass

from ...core.container import Container


@dataclass
class Column(Container):
    """Arrange child components vertically."""
