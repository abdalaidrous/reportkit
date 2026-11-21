import re
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
        "font_style": "font-style",
        "line_height": "line-height",
        "letter_spacing": "letter-spacing",
        "color": "color",
        "text_align": "text-align",
        "text_transform": "text-transform",
        "text_decoration": "text-decoration",
        "vertical_align": "vertical-align",
        "direction": "direction",
        "background_color": "background-color",
        "opacity": "opacity",
        "width": "width",
        "min_width": "min-width",
        "max_width": "max-width",
        "height": "height",
        "min_height": "min-height",
        "max_height": "max-height",
        "display": "display",
        "flex_direction": "flex-direction",
        "flex_wrap": "flex-wrap",
        "flex": "flex",
        "justify_content": "justify-content",
        "align_items": "align-items",
        "align_self": "align-self",
        "gap": "gap",
        "row_gap": "row-gap",
        "column_gap": "column-gap",
        "padding": "padding",
        "padding_top": "padding-top",
        "padding_right": "padding-right",
        "padding_bottom": "padding-bottom",
        "padding_left": "padding-left",
        "margin": "margin",
        "margin_top": "margin-top",
        "margin_right": "margin-right",
        "margin_bottom": "margin-bottom",
        "margin_left": "margin-left",
        "border_width": "border-width",
        "border_color": "border-color",
        "border_style": "border-style",
        "border_radius": "border-radius",
        "box_shadow": "box-shadow",
        "overflow": "overflow",
    }

    DIMENSIONS = {
        "font_size",
        "letter_spacing",
        "width",
        "min_width",
        "max_width",
        "height",
        "min_height",
        "max_height",
        "gap",
        "row_gap",
        "column_gap",
        "padding",
        "padding_top",
        "padding_right",
        "padding_bottom",
        "padding_left",
        "margin",
        "margin_top",
        "margin_right",
        "margin_bottom",
        "margin_left",
        "border_width",
        "border_radius",
    }

    KEYWORDS = {
        "font_style": {"normal", "italic", "oblique"},
        "text_align": {"start", "end", "left", "right", "center", "justify"},
        "text_transform": {"none", "uppercase", "lowercase", "capitalize"},
        "text_decoration": {"none", "underline", "overline", "line-through"},
        "direction": {"ltr", "rtl"},
        "display": {"block", "inline", "inline-block", "flex", "grid", "none"},
        "flex_direction": {"row", "row-reverse", "column", "column-reverse"},
        "flex_wrap": {"nowrap", "wrap", "wrap-reverse"},
        "justify_content": {"start", "end", "center", "space-between", "space-around", "space-evenly", "flex-start", "flex-end"},
        "align_items": {"start", "end", "center", "stretch", "baseline", "flex-start", "flex-end"},
        "align_self": {"auto", "start", "end", "center", "stretch", "baseline", "flex-start", "flex-end"},
        "vertical_align": {"baseline", "middle", "top", "bottom", "text-top", "text-bottom"},
        "border_style": {"none", "solid", "dashed", "dotted", "double"},
        "overflow": {"visible", "hidden", "auto", "scroll"},
    }

    DIMENSION_VALUE = re.compile(r"-?(?:\d+(?:\.\d+)?|\.\d+)(?:px|%|rem|em|mm|cm|in|pt|vw|vh)?$")

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

            if name == "opacity" and not 0 <= value <= 1:
                raise ValueError(f"Invalid CSS value for '{name}'.")

            return f"{value}px" if name in self.DIMENSIONS else str(value)

        if not isinstance(value, str):
            raise TypeError(f"Unsupported CSS value for '{name}'.")

        if any(character in value for character in (";", "{", "}", "<", ">", "\n", "\r", "\\")):
            raise ValueError(f"Invalid CSS value for '{name}'.")

        if name in self.KEYWORDS and value not in self.KEYWORDS[name]:
            raise ValueError(f"Invalid CSS value for '{name}'.")

        if name in self.DIMENSIONS and not self.DIMENSION_VALUE.fullmatch(value):
            raise ValueError(f"Invalid CSS value for '{name}'.")

        return value

    def to_attribute(self, style: Style) -> str:
        """
        Return escaped CSS declarations for an HTML attribute.
        """
        return escape(self.resolve(style), quote=True)
