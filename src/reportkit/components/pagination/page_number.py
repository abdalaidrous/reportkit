from dataclasses import dataclass

from ...core.component import Component


@dataclass(kw_only=True)
class PageNumber(Component):
    """Represent a page numbering placeholder."""

    format: str = "Page {page} of {pages}"

    def __post_init__(self):
        """Validate page number format."""
        if not isinstance(self.format, str):
            raise TypeError("Page number format must be a string.")
        if not self.format:
            raise ValueError("Page number format cannot be empty.")
