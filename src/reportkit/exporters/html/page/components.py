from dataclasses import dataclass, field

from ....components.document import Footer, Header, Page
from ....components.pagination import PageCount, PageNumber


@dataclass
class PageComponents:
    """
    Hold the components that affect print CSS.
    """

    pages: list = field(default_factory=list)
    numbers: list = field(default_factory=list)
    counts: list = field(default_factory=list)
    running: list = field(default_factory=list)


class HtmlPageComponentFinder:
    """
    Collect pages, page numbers, page counts and repeating headers/footers in one tree walk.
    """

    @classmethod
    def find(cls, document):
        """
        Walk the document once and return the collected components.
        """
        found = PageComponents()
        cls.collect(document, found)
        return found

    @classmethod
    def collect(cls, component, found):
        """
        Collect one component, then its children.
        """
        if isinstance(component, Page):
            found.pages.append(component)

        elif isinstance(component, PageNumber):
            found.numbers.append(component)

        elif isinstance(component, PageCount):
            found.counts.append(component)

        elif isinstance(component, (Header, Footer)) and component.repeat:
            found.running.append(component)

        for child in getattr(component, "children", []):
            cls.collect(child, found)
