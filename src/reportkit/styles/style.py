from dataclasses import dataclass, fields


@dataclass(frozen=True, kw_only=True)
class Style:
    """
    Define reusable visual properties for report components.
    """

    # Typography
    font_family: str | None = None
    font_size: float | None = None
    font_weight: str | int | None = None
    font_style: str | None = None
    line_height: float | None = None
    letter_spacing: float | None = None
    color: str | None = None
    text_align: str | None = None
    text_decoration: str | None = None
    text_transform: str | None = None
    vertical_align: str | None = None
    direction: str | None = None
    white_space: str | None = None

    # Layout
    display: str | None = None
    position: str | None = None
    top: float | None = None
    right: float | None = None
    bottom: float | None = None
    left: float | None = None
    width: float | None = None
    min_width: float | None = None
    max_width: float | None = None
    height: float | None = None
    min_height: float | None = None
    max_height: float | None = None
    flex_direction: str | None = None
    flex_wrap: str | None = None
    flex: str | float | None = None
    flex_grow: float | None = None
    flex_shrink: float | None = None
    justify_content: str | None = None
    align_items: str | None = None
    align_content: str | None = None
    align_self: str | None = None
    gap: float | None = None
    row_gap: float | None = None
    column_gap: float | None = None
    grid_template_columns: str | None = None
    grid_template_rows: str | None = None
    grid_column: str | None = None
    grid_row: str | None = None
    background_color: str | None = None
    opacity: float | None = None

    # Spacing
    padding: float | None = None
    padding_top: float | None = None
    padding_right: float | None = None
    padding_bottom: float | None = None
    padding_left: float | None = None
    margin: float | None = None
    margin_top: float | None = None
    margin_right: float | None = None
    margin_bottom: float | None = None
    margin_left: float | None = None

    # Borders
    border_width: float | None = None
    border_color: str | None = None
    border_style: str | None = None
    border_radius: float | None = None
    border_top: str | None = None
    border_right: str | None = None
    border_bottom: str | None = None
    border_left: str | None = None

    # Effects
    box_shadow: str | None = None
    overflow: str | None = None

    def merge(self, other: "Style") -> "Style":
        """
        Merge styles while prioritizing explicitly defined values.
        """
        if not isinstance(other, Style):
            raise TypeError("Expected a Style instance.")

        values = self.to_dict()
        values.update(other.to_dict())
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
