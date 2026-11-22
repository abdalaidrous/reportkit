from dataclasses import dataclass

from ...core.component import Component
from ...validators.media.image import ImageValidator


@dataclass(kw_only=True)
class Image(Component):
    """
    Represent an image in a report.
    """

    src: str
    alt: str = ""
    width: str | None = None
    height: str | None = None
    fit: str = "contain"

    def __post_init__(self):
        """
        Validate image properties.
        """
        ImageValidator.validate(self)
