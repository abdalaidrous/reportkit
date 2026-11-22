from dataclasses import dataclass

from ...core.component import Component
from ...validators.pagination.page_number import PageNumberValidator


@dataclass(kw_only=True)
class PageNumber(Component):
    """
    Represent a page numbering placeholder.
    """

    format: str = "Page {page} of {pages}"

    def __post_init__(self):
        """
        Validate the page number format.
        """
        PageNumberValidator.validate(self)
