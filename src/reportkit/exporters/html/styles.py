from html import escape
from math import isfinite
from numbers import Real

from ...styles.style import Style


class HtmlStyleResolver:
    """
    Convert component styles into safe CSS declarations.
    """

    PROPERTIES = {
        "font_family": "font-family",
        "font_size": "font-size",
        "font_weight": "font-weight",
        "color": "color",
        "background_color": "background-color",
        "text_align": "text-align",
        "vertical_align": "vertical-align",
        "direction": "direction",
        "width": "width",
        "height": "height",
        "padding": "padding",
        "margin": "margin",
        "border_width": "border-width",
        "border_color": "border-color",
        "border_style": "border-style",
    }

    DIMENSIONS = {
        "font_size",
        "width",
        "height",
        "padding",
        "margin",
        "border_width",
    }

    def resolve(self, style: Style) -> str:
        """
        Convert a Style instance into CSS declarations.
        """
        if not isinstance(style, Style):
            raise TypeError("Expected a Style instance.")

        declarations = []
        for name, value in style.to_dict().items():
            property_name = self.PROPERTIES.get(name)
            if property_name is None or value is None:
                continue

            value = self.format_value(name, value)
            declarations.append(f"{property_name}: {value}")

        return "; ".join(declarations)

    def format_value(self, name: str, value) -> str:
        """
        Format and validate a CSS property value.
        """
        if isinstance(value, bool):
            raise ValueError(f"Invalid CSS value for '{name}'.")

        if isinstance(value, Real):
            if not isfinite(value):
                raise ValueError(f"Invalid CSS value for '{name}'.")

            return f"{value}px" if name in self.DIMENSIONS else str(value)

        if not isinstance(value, str):
            raise TypeError(f"Unsupported CSS value for '{name}'.")

        if any(character in value for character in (";", "{", "}", "<", ">", "\n", "\r", "\\")):
            raise ValueError(f"Invalid CSS value for '{name}'.")

        return value

    def to_attribute(self, style: Style) -> str:
        """
        Return escaped CSS declarations for an HTML attribute.
        """
        return escape(self.resolve(style), quote=True)
