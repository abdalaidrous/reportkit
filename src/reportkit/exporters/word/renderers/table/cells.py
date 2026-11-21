from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT

from .....components.table import TableCell
from .....styles.borders import edge_borders
from .....styles.style import Style
from ...styles.text import write_paragraph
from ...styles.xml import SIDES, set_borders, set_cell_width, set_shading
from ...values import cell_text


def fill_cell(cell, text, style, direction):
    """
    Write a cell's text with its style, background and borders.
    """
    properties = cell._tc.get_or_add_tcPr()
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    if style.background_color:
        set_shading(properties, style.background_color)
    set_borders(properties, "w:tcBorders", dict(zip(SIDES, edge_borders(style))))
    write_paragraph(cell.paragraphs[0], text, style, direction)


def prepare_entry(entry):
    """
    Return the text and the cell style (alignment and explicit cell style) of one entry.
    """
    content, column = entry
    align = Style(text_align=column.align) if column else Style()
    if isinstance(content, TableCell):
        return cell_text(content, column), (Style(text_align=content.align) if content.align else align).merge(content.style)
    return cell_text(content, column), align


def size_row(row, widths):
    """
    Give every cell of a new row its column width.
    """
    for cell, width in zip(row.cells, widths):
        set_cell_width(cell, width)
