from dataclasses import dataclass

from ...core.container import Container


@dataclass
class Column(Container):
    """Arrange child components vertically."""

    align: str | None = None
    justify: str | None = None
    gap: str | None = None
    direction: str | None = None
