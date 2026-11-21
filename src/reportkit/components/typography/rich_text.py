from dataclasses import dataclass, field

from ...core.component import Component
from .text_span import TextSpan


@dataclass(kw_only=True)
class RichText(Component):
    """Represent text containing multiple styled fragments."""

    spans: list[TextSpan] = field(default_factory=list)
    align: str = "start"

    def __post_init__(self):
        """Validate rich text configuration."""
        if not all(isinstance(span, TextSpan) for span in self.spans):
            raise TypeError("RichText spans must contain TextSpan instances.")
        if self.align not in {"start", "center", "end", "left", "right"}:
            raise ValueError("Unsupported text alignment.")
