from dataclasses import dataclass, field

from ...styles.style import Style


@dataclass(frozen=True, kw_only=True)
class TextSpan:
    """
    Represent one styled text fragment.
    """

    value: str
    style: Style = field(default_factory=Style)
    language: str | None = None
    direction: str | None = None

    def __post_init__(self):
        """
        Validate text fragment properties.
        """
        if not isinstance(self.value, str):
            raise TypeError("TextSpan value must be a string.")
        if self.direction not in {None, "ltr", "rtl", "auto"}:
            raise ValueError("Unsupported text direction.")
