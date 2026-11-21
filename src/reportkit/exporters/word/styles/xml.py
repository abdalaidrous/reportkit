import re

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from ..exceptions import WordExportError


BORDER_LINES = {"solid": "single", "dashed": "dashed", "dotted": "dotted", "double": "double", "none": "nil"}
SIDES = ("left", "right", "top", "bottom")

SCHEMA_ORDER = {
    "pPr": ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"],
    "rPr": ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline", "shadow", "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing", "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText", "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath"],
    "tcPr": ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark"],
    "tblPr": ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook"],
    "trPr": ["cnfStyle", "divId", "gridBefore", "gridAfter", "wBefore", "wAfter", "cantSplit", "trHeight", "tblHeader", "tblCellSpacing", "jc", "hidden"],
    "tcBorders": ["top", "start", "left", "bottom", "end", "right", "insideH", "insideV", "tl2br", "tr2bl"],
    "tblBorders": ["top", "start", "left", "bottom", "end", "right", "insideH", "insideV"],
    "tblCellMar": ["top", "start", "left", "bottom", "end", "right"],
    "pBdr": ["top", "left", "bottom", "right", "between", "bar"],
}


def child(parent, tag):
    """
    Return an existing XML child or create it in schema order.
    """
    element = parent.find(qn(tag))

    if element is not None:
        return element

    element = OxmlElement(tag)
    position = get_child_position(parent, tag)
    parent.insert(position, element)

    return element


def get_child_position(parent, tag):
    """
    Resolve the insertion position based on the Word XML schema.
    """
    parent_name = parent.tag.split("}")[-1]
    order = SCHEMA_ORDER[parent_name]
    successors = get_successor_tags(order, tag)

    return next((index for index, element in enumerate(parent) if element.tag in successors), len(parent))


def get_successor_tags(order, tag):
    """
    Return the XML tags that must follow the requested child.
    """
    position = order.index(tag.split(":")[-1])
    return {qn(f"w:{name}") for name in order[position + 1:]}


def set_attributes(element, **values):
    """
    Apply Word XML attributes to an element.
    """
    for name, value in values.items():
        element.set(qn(f"w:{name}"), str(value))

    return element


def hex_color(color):
    """
    Convert CSS hexadecimal colors into Word RGB format.
    """
    match = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", (color or "").strip())

    if not match:
        raise WordExportError(f"Word export supports #rgb and #rrggbb colors only, got {color!r}.")

    digits = match.group(1)
    return (digits if len(digits) == 6 else "".join(character * 2 for character in digits)).upper()


def border_attributes(value):
    """
    Convert a CSS border into Word border attributes.
    """
    width, line, color = (value.split() + ["", "", ""])[:3]
    pixels = float(re.sub(r"[^\d.]", "", width) or 1)

    return {
        "val": BORDER_LINES.get(line, "single"),
        "sz": max(2, round(pixels * 0.75 * 8)),
        "space": 0,
        "color": hex_color(color) if color else "auto",
    }


def set_borders(properties, container_tag, sides):
    """
    Apply CSS borders to a Word XML border container.
    """
    borders = child(properties, container_tag)

    for side, value in sides.items():
        if value:
            set_border(borders, side, value)


def set_border(borders, side, value):
    """
    Apply a single border with its Word attributes.
    """
    element = child(borders, f"w:{side}")
    set_attributes(element, **border_attributes(value))


def set_shading(properties, color):
    """
    Apply a background color to a Word element.
    """
    shading = child(properties, "w:shd")
    set_attributes(shading, val="clear", color="auto", fill=hex_color(color))


def set_cell_width(cell, width):
    """
    Apply a fixed cell width in twips.
    """
    properties = cell._tc.get_or_add_tcPr()
    set_attributes(child(properties, "w:tcW"), w=int(width.twips), type="dxa")


def set_bidi_table(table):
    """
    Apply right-to-left layout to a table.
    """
    child(table._tbl.tblPr, "w:bidiVisual")


def set_fixed_layout(table):
    """
    Disable automatic table column resizing.
    """
    set_attributes(child(table._tbl.tblPr, "w:tblLayout"), type="fixed")


def clear_table_borders(table):
    """
    Remove all outer and inner table borders.
    """
    borders = {side: "0px none" for side in (*SIDES, "insideH", "insideV")}
    set_borders(table._tbl.tblPr, "w:tblBorders", borders)


def set_cell_margins(table, vertical):
    """
    Apply vertical padding to all table cells.
    """
    margins = child(table._tbl.tblPr, "w:tblCellMar")

    for side in ("top", "bottom"):
        set_attributes(child(margins, f"w:{side}"), w=vertical, type="dxa")


def set_row_flags(row, repeat_header=False, cant_split=False):
    """
    Apply header repetition and page splitting flags.
    """
    properties = row._tr.get_or_add_trPr()

    if repeat_header:
        child(properties, "w:tblHeader")

    if cant_split:
        child(properties, "w:cantSplit")


def set_bidi_paragraph(paragraph):
    """
    Apply right-to-left direction to a paragraph.
    """
    child(paragraph._p.get_or_add_pPr(), "w:bidi")


def add_field(paragraph, instruction):
    """
    Append a Word field with its initial display value.
    """
    field = create_field(instruction)
    paragraph._p.append(field)


def create_field(instruction):
    """
    Create a Word field with its instruction and result run.
    """
    field = set_attributes(OxmlElement("w:fldSimple"), instr=instruction)
    field.append(create_field_run())
    return field


def create_field_run():
    """
    Create the initial result run for a Word field.
    """
    run = OxmlElement("w:r")
    text = OxmlElement("w:t")
    text.text = "1"
    run.append(text)
    return run