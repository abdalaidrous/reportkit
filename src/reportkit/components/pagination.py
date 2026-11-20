from dataclasses import dataclass

from ..core.component import Component


@dataclass
class PageBreak(Component):
    """
    Represent an explicit page break.
    """


@dataclass
class PageNumber(Component):
    """
    Represent the current page number.
    """


@dataclass
class PageCount(Component):
    """
    Represent the total number of pages.
    """
