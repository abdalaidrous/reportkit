from dataclasses import dataclass

from ...core.component import Component


@dataclass
class PageCount(Component):
    """
    Represent the total number of pages.
    """
