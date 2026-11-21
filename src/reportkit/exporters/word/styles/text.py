from copy import deepcopy
from functools import lru_cache

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from ....styles.style import Style
from ....styles.tokens import token
from ...html.direction import text_direction
from .xml import child, hex_color, set_attributes, set_bidi_paragraph


DEFAULT_FONT = "Arial"
TEMPLATES = 4096

ALIGNMENTS = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
}


def write_paragraph(paragraph, text, style, direction):
    """
    Render paragraph text while preserving explicit line breaks.
    """
    format_paragraph(paragraph, style, direction)

    for index, line in enumerate(str(text).split("\n")):
        run = paragraph.add_run()

        if index:
            run.add_break()

        run.add_text(line)
        format_run(run, style, text_direction(line) or "ltr")

    return paragraph


def add_run(paragraph, text, style, direction):
    """
    Add a styled text run with its detected direction.
    """
    run = paragraph.add_run(text)
    format_run(run, style, text_direction(text) or "ltr")
    return run


def format_paragraph(paragraph, style, direction):
    """
    Apply cached paragraph properties or format existing properties.
    """
    if paragraph._p.pPr is None:
        paragraph._p.insert(0, deepcopy(paragraph_template(style.text_align, direction)))
        return

    apply_paragraph_format(paragraph, style, direction)


@lru_cache(maxsize=TEMPLATES)
def paragraph_template(align, direction):
    """
    Build reusable paragraph properties for alignment and direction.
    """
    paragraph = Paragraph(OxmlElement("w:p"), None)
    apply_paragraph_format(paragraph, Style(text_align=align), direction)
    return paragraph._p.pPr


def apply_paragraph_format(paragraph, style, direction):
    """
    Apply paragraph direction, alignment, and spacing.
    """
    if direction == "rtl":
        set_bidi_paragraph(paragraph)

    paragraph.alignment = get_alignment(style.text_align, direction)
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)


def format_run(run, style, direction):
    """
    Apply cached run properties or format existing properties.
    """
    if run._r.rPr is None:
        run._r.insert(0, deepcopy(run_template(style, direction)))
        return

    apply_run_format(run, style, direction)


@lru_cache(maxsize=TEMPLATES)
def run_template(style, direction):
    """
    Build reusable run properties for style and direction.
    """
    run = Run(OxmlElement("w:r"), None)
    apply_run_format(run, style, direction)
    return run._r.rPr


def apply_run_format(run, style, direction):
    """
    Apply font formatting and complex-script properties.
    """
    family = get_font_family(style)
    size = points(style.font_size or token("--rk-font-md"))

    apply_font(run, style, family, size)
    apply_font_color(run, style)
    apply_complex_script(run, family, size, direction)


def get_font_family(style):
    """
    Resolve the primary font family.
    """
    return (style.font_family or DEFAULT_FONT).split(",")[0].strip(" '\"")


def apply_font(run, style, family, size):
    """
    Apply font family, size, weight, and style.
    """
    run.font.name = family
    run.font.size = Pt(size)
    run.font.bold = is_bold(style.font_weight)
    run.font.italic = style.font_style == "italic"


def apply_font_color(run, style):
    """
    Apply the configured font color.
    """
    if style.color:
        run.font.color.rgb = RGBColor.from_string(hex_color(style.color))


def apply_complex_script(run, family, size, direction):
    """
    Apply font properties for Arabic and complex-script text.
    """
    properties = run._r.get_or_add_rPr()

    set_attributes(child(properties, "w:rFonts"), ascii=family, hAnsi=family, cs=family)
    set_attributes(child(properties, "w:szCs"), val=round(size * 2))

    if run.font.bold:
        child(properties, "w:bCs")

    if direction == "rtl":
        child(properties, "w:rtl")


def get_alignment(align, direction):
    """
    Resolve CSS text alignment for Word paragraph direction.
    """
    if not align:
        return None

    sides = get_alignment_sides(direction)
    return ALIGNMENTS.get(sides.get(align, align))


def get_alignment_sides(direction):
    """
    Resolve logical and physical alignment sides.
    """
    if direction == "rtl":
        return {"start": "left", "end": "right", "left": "right", "right": "left"}

    return {"start": "left", "end": "right"}


def points(size):
    """
    Convert CSS pixel or point values into points.
    """
    text = str(size)
    number = float("".join(character for character in text if character.isdigit() or character == "."))
    return round(number if text.endswith("pt") else number * 0.75, 1)


def is_bold(weight):
    """
    Check whether the configured font weight is bold.
    """
    return weight == "bold" or (str(weight).isdigit() and int(weight) >= 600)


def add_page_break(paragraph):
    """
    Insert a page break after the paragraph.
    """
    paragraph.add_run().add_break(WD_BREAK.PAGE)