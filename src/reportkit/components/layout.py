from dataclasses import dataclass

from ..core.component import Component, Container


@dataclass
class Section(Container):
    """
    Group related report components.
    """


@dataclass
class Row(Container):
    """
    Arrange child components horizontally.
    """


@dataclass
class Column(Container):
    """
    Arrange child components vertically.
    """


@dataclass
class Grid(Container):
    """
    Arrange child components in a grid.
    """

    columns: int = 1


@dataclass
class Spacer(Component):
    """
    Represent empty space between components.
    """

    height: float = 0


@dataclass
class Divider(Component):
    """
    Represent a visual separator.
    """
