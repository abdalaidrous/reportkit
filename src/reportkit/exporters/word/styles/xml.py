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
    Return the first child with a tag, creating it at its schema position when missing (Word rejects misordered XML).
    """
    found = parent.find(qn(tag))
    if found is None:
        found, order = OxmlElement(tag), SCHEMA_ORDER[parent.tag.split("}")[1]]
        successors = {qn(f"w:{name}") for name in order[order.index(tag[2:]) + 1:]}
        position = next((index for index, existing in enumerate(parent) if existing.tag in successors), len(parent))
        parent.insert(position, found)
    return found


def set_attributes(element, **values):
    """
    Set w: attributes on an element.
    """
    for name, value in values.items():
        element.set(qn(f"w:{name}"), str(value))
    return element


def hex_color(color):
    """
    Convert a #rgb or #rrggbb color into the RRGGBB form Word uses.
    """
    match = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", (color or "").strip())
    if not match:
        raise WordExportError(f"Word export supports #rgb and #rrggbb colors only, got {color!r}.")
    digits = match.group(1)
    return (digits if len(digits) == 6 else "".join(character * 2 for character in digits)).upper()


def border_attributes(value):
    """
    Convert a CSS border such as "1px solid #dddddd" into Word border attributes (size in eighths of a point).
    """
    width, line, color = (value.split() + ["", "", ""])[:3]
    pixels = float(re.sub(r"[^\d.]", "", width) or 1)
    return {"val": BORDER_LINES.get(line, "single"), "sz": max(2, round(pixels * 0.75 * 8)), "space": 0, "color": hex_color(color) if color else "auto"}


def set_borders(properties, container_tag, sides):
    """
    Write the given CSS borders (side name to value) into a tcBorders, tblBorders or pBdr element.
    """
    borders = child(properties, container_tag)
    for side, value in sides.items():
        if value:
            set_attributes(child(borders, f"w:{side}"), **border_attributes(value))


def set_shading(properties, color):
    """
    Fill a cell or paragraph background.
    """
    set_attributes(child(properties, "w:shd"), val="clear", color="auto", fill=hex_color(color))


def set_cell_width(cell, width):
    """
    Fix a cell width in twips, since Word ignores column widths alone.
    """
    set_attributes(child(cell._tc.get_or_add_tcPr(), "w:tcW"), w=int(width.twips), type="dxa")


def set_bidi_table(table):
    """
    Lay a table out right to left, so its first column sits on the right.
    """
    child(table._tbl.tblPr, "w:bidiVisual")


def set_fixed_layout(table):
    """
    Keep the declared column widths instead of Word's automatic fit.
    """
    set_attributes(child(table._tbl.tblPr, "w:tblLayout"), type="fixed")


def clear_table_borders(table):
    """
    Remove every table border, for layout grids.
    """
    set_borders(table._tbl.tblPr, "w:tblBorders", {side: "0px none" for side in (*SIDES, "insideH", "insideV")})


def set_cell_margins(table, vertical):
    """
    Pad every cell of a table above and below, in twips.
    """
    margins = child(table._tbl.tblPr, "w:tblCellMar")
    for side in ("top", "bottom"):
        set_attributes(child(margins, f"w:{side}"), w=vertical, type="dxa")


def set_row_flags(row, repeat_header=False, cant_split=False):
    """
    Mark a row as a repeated header and/or as not splitting across pages.
    """
    properties = row._tr.get_or_add_trPr()
    if repeat_header:
        child(properties, "w:tblHeader")
    if cant_split:
        child(properties, "w:cantSplit")


def set_bidi_paragraph(paragraph):
    """
    Make a paragraph right to left.
    """
    child(paragraph._p.get_or_add_pPr(), "w:bidi")


def add_field(paragraph, instruction):
    """
    Append a simple field such as PAGE or NUMPAGES.
    """
    field = set_attributes(OxmlElement("w:fldSimple"), instr=instruction)
    run = OxmlElement("w:r")
    text = OxmlElement("w:t")
    text.text = "1"
    run.append(text)
    field.append(run)
    paragraph._p.append(field)
