import re
from functools import cache
from typing import NamedTuple

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from ...styles.style import Style
from ..html.templates import HtmlTemplateEngine
from .exceptions import ExcelExportError

TOKEN_PATTERN = re.compile(r"(--rk-[\w-]+)\s*:\s*([^;]+);")
VERTICAL = {"top": "top", "middle": "center", "bottom": "bottom"}


@cache
def load_tokens():
    """
    Read the design tokens from tokens.css so Excel reuses the HTML visual identity.
    """
    raw = dict(TOKEN_PATTERN.findall((HtmlTemplateEngine().static_dir / "tokens.css").read_text(encoding="utf-8")))
    return {name: resolve_token(value.strip(), raw) for name, value in raw.items()}


def resolve_token(value, raw):
    """
    Resolve var(--name) references inside a token value.
    """
    return re.sub(r"var\((--rk-[\w-]+)\)", lambda match: resolve_token(raw[match.group(1)].strip(), raw), value)


def token(name):
    """
    Return one design token value.
    """
    return load_tokens()[name]


class CellFormat(NamedTuple):
    """
    Hold the openpyxl style objects for one cell.
    """

    font: Font
    fill: PatternFill | None
    alignment: Alignment
    border: Border

    def apply(self, cell):
        """
        Apply the format to a worksheet cell.
        """
        cell.font, cell.alignment, cell.border = self.font, self.alignment, self.border
        if self.fill:
            cell.fill = self.fill


@cache
def get_format(style, direction):
    """
    Convert a ReportKit Style into openpyxl objects; cached because reports reuse a few styles many times.
    """
    return CellFormat(get_font(style), get_fill(style.background_color), get_alignment(style, direction), get_border(style))


def get_font(style):
    """
    Build the font from the typography properties.
    """
    family = style.font_family.split(",")[0].strip(" '\"") if style.font_family else None
    size = points(style.font_size) if style.font_size else None
    return Font(name=family, size=size, bold=is_bold(style.font_weight), italic=style.font_style == "italic", color=get_color(style.color))


def get_fill(color):
    """
    Build a solid fill for a background color.
    """
    return PatternFill("solid", fgColor=get_color(color)) if color else None


def get_alignment(style, direction):
    """
    Build the alignment, resolving start/end against the sheet direction.
    """
    return Alignment(horizontal=get_horizontal(style.text_align, direction), vertical=VERTICAL.get(style.vertical_align, "center"), wrap_text=True)


def get_horizontal(align, direction):
    """
    Map CSS text-align to Excel horizontal alignment.
    """
    sides = {"start": "right", "end": "left"} if direction == "rtl" else {"start": "left", "end": "right"}
    return sides.get(align, align if align in ("left", "right", "center", "justify") else None)


def get_border(style):
    """
    Build the border from the shorthand border properties.
    """
    whole = f"{style.border_width or 1}px {style.border_style or 'solid'} {style.border_color}" if style.border_color else None
    sides = [get_side(side or whole) for side in (style.border_left, style.border_right, style.border_top, style.border_bottom)]
    return Border(left=sides[0], right=sides[1], top=sides[2], bottom=sides[3])


def get_side(value):
    """
    Convert a CSS border such as "1px solid #dddddd" into an Excel side.
    """
    if not value:
        return Side()
    width, line, color = (value.split() + ["", "", ""])[:3]
    weight = float(re.sub(r"[^\d.]", "", width) or 1)
    kind = "dashed" if line == "dashed" else "dotted" if line == "dotted" else "double" if line == "double" else "thick" if weight >= 3 else "medium" if weight >= 2 else "thin"
    return Side(style=kind, color=get_color(color) if color else None)


def get_color(color):
    """
    Convert a #rgb or #rrggbb color into an Excel ARGB color.
    """
    if not color:
        return None
    match = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", color.strip())
    if not match:
        raise ExcelExportError(f"Excel export supports #rgb and #rrggbb colors only, got {color!r}.")
    digits = match.group(1) if len(match.group(1)) == 6 else "".join(character * 2 for character in match.group(1))
    return "FF" + digits.upper()


def points(size):
    """
    Convert a CSS font size (number of px, "12px" or "9pt") into Excel points.
    """
    text = str(size)
    return round(float(re.sub(r"[^\d.]", "", text)) * (1 if text.endswith("pt") else 0.75), 1)


def is_bold(weight):
    """
    Return whether a CSS font weight is bold.
    """
    return weight == "bold" or (str(weight).isdigit() and int(weight) >= 600)


def table_styles():
    """
    Build the table styles from the shared table tokens.
    """
    divider, frame = f"1px solid {token('--rk-table-divider-color')}", f"1px solid {token('--rk-table-frame-color')}"
    return {
        "cell": Style(color=token("--rk-table-cell-color"), border_bottom=divider),
        "bordered": Style(border_left=divider, border_right=divider, border_top=divider, border_bottom=divider),
        "header": Style(background_color=token("--rk-table-header-bg"), color=token("--rk-table-header-color"), font_weight=700, border_top=f"1px solid {token('--rk-table-header-accent')}", border_bottom=f"2px solid {token('--rk-table-header-rule')}", border_left=frame, border_right=frame),
        "ruled": Style(border_top=f"1px solid {token('--rk-table-ruled-color')}", border_bottom=f"2px solid {token('--rk-table-ruled-color')}"),
        "stripe": Style(background_color=token("--rk-table-stripe-bg")),
        "total": Style(background_color=token("--rk-table-total-bg"), font_weight=700, border_top=f"2px solid {token('--rk-table-divider-color')}"),
        "subtotal": Style(background_color=token("--rk-table-subtotal-bg"), font_weight=600),
        "group-header": Style(background_color=token("--rk-table-group-bg"), font_weight=700),
        "data": Style(),
        "compact": Style(font_size=float(token("--rk-font-xs").removesuffix("px"))),
    }
