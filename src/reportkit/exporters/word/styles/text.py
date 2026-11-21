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
ALIGNMENTS = {"left": WD_ALIGN_PARAGRAPH.LEFT, "right": WD_ALIGN_PARAGRAPH.RIGHT, "center": WD_ALIGN_PARAGRAPH.CENTER, "justify": WD_ALIGN_PARAGRAPH.JUSTIFY}


def write_paragraph(paragraph, text, style, direction):
    """
    Fill a paragraph with text (explicit line breaks kept) in the given style and direction.
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
    Append one styled run; text without letters (numbers, dates) stays left to right so it is not reordered.
    """
    run = paragraph.add_run(text)
    format_run(run, style, text_direction(text) or "ltr")
    return run


def format_paragraph(paragraph, style, direction):
    """
    Apply direction, alignment and spacing to a paragraph; a paragraph without properties gets a copy of the
    properties built once for the same alignment and direction (large tables repeat them on every row).
    """
    if paragraph._p.pPr is None:
        paragraph._p.insert(0, deepcopy(paragraph_template(style.text_align, direction)))
        return
    apply_paragraph_format(paragraph, style, direction)


@lru_cache(maxsize=TEMPLATES)
def paragraph_template(align, direction):
    """
    Build the paragraph properties for one alignment and direction.
    """
    paragraph = Paragraph(OxmlElement("w:p"), None)
    apply_paragraph_format(paragraph, Style(text_align=align), direction)
    return paragraph._p.pPr


def apply_paragraph_format(paragraph, style, direction):
    """
    Write direction, alignment and spacing into the paragraph properties.
    """
    if direction == "rtl":
        set_bidi_paragraph(paragraph)
    paragraph.alignment = get_alignment(style.text_align, direction)
    paragraph.paragraph_format.space_before, paragraph.paragraph_format.space_after = Pt(0), Pt(0)


def format_run(run, style, direction):
    """
    Apply the font, size, weight, slant and color to a run, for Latin and Arabic (complex script) text alike; a run
    without properties gets a copy of the properties built once for the same style and direction.
    """
    if run._r.rPr is None:
        run._r.insert(0, deepcopy(run_template(style, direction)))
        return
    apply_run_format(run, style, direction)


@lru_cache(maxsize=TEMPLATES)
def run_template(style, direction):
    """
    Build the run properties for one style and direction.
    """
    run = Run(OxmlElement("w:r"), None)
    apply_run_format(run, style, direction)
    return run._r.rPr


def apply_run_format(run, style, direction):
    """
    Write the font, size, weight, slant and color into the run properties.
    """
    family, size = (style.font_family or DEFAULT_FONT).split(",")[0].strip(" '\""), points(style.font_size or token("--rk-font-md"))
    run.font.name, run.font.size, run.font.bold, run.font.italic = family, Pt(size), is_bold(style.font_weight), style.font_style == "italic"
    if style.color:
        run.font.color.rgb = RGBColor.from_string(hex_color(style.color))
    properties = run._r.get_or_add_rPr()
    set_attributes(child(properties, "w:rFonts"), ascii=family, hAnsi=family, cs=family)
    set_attributes(child(properties, "w:szCs"), val=round(size * 2))
    if run.font.bold:
        child(properties, "w:bCs")
    if direction == "rtl":
        child(properties, "w:rtl")


def get_alignment(align, direction):
    """
    Map CSS text-align to Word; in right-to-left paragraphs Word mirrors left and right.
    """
    sides = {"start": "left", "end": "right"} if direction == "ltr" else {"start": "left", "end": "right", "left": "right", "right": "left"}
    return ALIGNMENTS.get(sides.get(align, align)) if align else None


def points(size):
    """
    Convert a CSS size (number of px, "12px" or "9pt") into points.
    """
    text = str(size)
    number = float("".join(character for character in text if character.isdigit() or character == "."))
    return round(number if text.endswith("pt") else number * 0.75, 1)


def is_bold(weight):
    """
    Return whether a CSS font weight is bold.
    """
    return weight == "bold" or (str(weight).isdigit() and int(weight) >= 600)


def add_page_break(paragraph):
    """
    Start a new page after a paragraph.
    """
    paragraph.add_run().add_break(WD_BREAK.PAGE)
