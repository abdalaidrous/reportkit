from dataclasses import dataclass

from ...core.component import Component


@dataclass(kw_only=True)
class PageBreak(Component):
    """Insert a page break before the next content."""
