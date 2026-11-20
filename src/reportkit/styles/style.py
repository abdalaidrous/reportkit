from dataclasses import dataclass, fields


@dataclass(frozen=True, kw_only=True)
class Style:
    """
    Define reusable visual properties for report components.
    """

    font_family: str | None = None
    font_size: float | None = None
    font_weight: str | None = None
    color: str | None = None
    background_color: str | None = None
    text_align: str | None = None
    vertical_align: str | None = None
    direction: str | None = None
    width: float | None = None
    height: float | None = None
    padding: float | None = None
    margin: float | None = None
    border_width: float | None = None
    border_color: str | None = None
    border_style: str | None = None

    def merge(self, other: "Style") -> "Style":
        """
        Merge styles, prioritizing explicitly defined values.
        """
        if not isinstance(other, Style):
            raise TypeError("Expected a Style instance.")

        values = {field.name: getattr(self, field.name) for field in fields(self)}
        values.update({
            field.name: getattr(other, field.name)
            for field in fields(other)
            if getattr(other, field.name) is not None
        })
        return Style(**values)

    def to_dict(self) -> dict:
        """
        Return explicitly defined style properties.
        """
        return {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if getattr(self, field.name) is not None
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Style":
        """
        Create a style from a dictionary.
        """
        if not isinstance(data, dict):
            raise TypeError("Style definition must be a dictionary.")

        allowed = {field.name for field in fields(cls)}
        unknown = set(data) - allowed
        if unknown:
            raise ValueError(f"Unknown style properties: {', '.join(sorted(unknown))}")

        return cls(**data)
