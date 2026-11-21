from dataclasses import dataclass

from ...core.container import Container


@dataclass(kw_only=True)
class Page(Container):
    """Define a report page and its print settings."""

    size: str = "A4"
    orientation: str = "portrait"
    margin_top: str = "15mm"
    margin_right: str = "15mm"
    margin_bottom: str = "15mm"
    margin_left: str = "15mm"
    page_number_position: str = "bottom-center"

    def __post_init__(self):
        """Validate page settings."""
        super().__post_init__()
        if self.size not in {"A4", "A3", "A5", "Letter", "Legal"}:
            raise ValueError("Unsupported page size.")
        if self.orientation not in {"portrait", "landscape"}:
            raise ValueError("Unsupported page orientation.")
        if self.page_number_position not in {"top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right"}:
            raise ValueError("Unsupported page number position.")
