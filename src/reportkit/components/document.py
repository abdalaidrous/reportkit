from dataclasses import dataclass

from ..core.component import Container


@dataclass
class Report(Container):
    """
    Represent the root report document.
    """

    title: str = ""


@dataclass
class Page(Container):
    """
    Represent a report page.
    """


@dataclass
class Header(Container):
    """
    Represent a report header.
    """


@dataclass
class Footer(Container):
    """
    Represent a report footer.
    """
