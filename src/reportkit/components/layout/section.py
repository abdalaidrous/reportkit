from dataclasses import dataclass

from ...core.container import Container


@dataclass
class Section(Container):
    """
    Group related report components.
    """
