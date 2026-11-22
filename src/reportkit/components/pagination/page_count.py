from dataclasses import dataclass

from ...core.component import Component
from ...validators.pagination.page_count import PAGES, PageCountValidator


@dataclass(kw_only=True)
class PageCount(Component):
    """
    Show the total number of printed pages as a line of text, in the content or in a repeating Header or Footer.
    """

    format: str = PAGES

    def __post_init__(self):
        """
        Validate the page count format.
        """
        PageCountValidator.validate(self)

    @property
    def parts(self) -> tuple[str, str]:
        """
        Return the text before and after the page total.
        """
        before, _, after = self.format.partition(PAGES)
        return before, after
