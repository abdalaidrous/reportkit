from dataclasses import dataclass

from ...core.container import Container


@dataclass(kw_only=True)
class Box(Container):
    """
    Represent a styled container for report components.
    """
