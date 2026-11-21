from dataclasses import dataclass

from ...core.component import Component


@dataclass(kw_only=True)
class Image(Component):
    """Represent an image in a report."""

    src: str
    alt: str = ""
    width: str | None = None
    height: str | None = None
    fit: str = "contain"

    def __post_init__(self):
        """Validate image properties."""
        if not isinstance(self.src, str) or not self.src.strip():
            raise ValueError("Image source must be a non-empty string.")
        if self.fit not in {"contain", "cover", "fill", "none", "scale-down"}:
            raise ValueError("Unsupported image fit.")
