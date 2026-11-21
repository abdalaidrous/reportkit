from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT

from .....components.table import TableCell
from .....styles.borders import edge_borders
from .....styles.style import Style
from ...styles.text import write_paragraph
from ...styles.xml import SIDES, set_borders, set_cell_width, set_shading
from ...values import cell_text


def fill_cell(cell, text, style, direction):
    """
    Render cell content with its style, background, and borders.
    """
    properties = cell._tc.get_or_add_tcPr()
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    apply_cell_background(properties, style)
    apply_cell_borders(properties, style)
    write_paragraph(cell.paragraphs[0], text, style, direction)


def apply_cell_background(properties, style):
    """
    Apply the cell background color.
    """
    if style.background_color:
        set_shading(properties, style.background_color)


def apply_cell_borders(properties, style):
    """
    Apply the cell borders.
    """
    borders = dict(zip(SIDES, edge_borders(style)))
    set_borders(properties, "w:tcBorders", borders)


def prepare_entry(entry):
    """
    Resolve the entry text and cell style.
    """
    content, column = entry
    style = get_column_style(column)

    if isinstance(content, TableCell):
        style = get_cell_style(content, style)

    return cell_text(content, column), style


def get_column_style(column):
    """
    Resolve the column alignment style.
    """
    return Style(text_align=column.align) if column else Style()


def get_cell_style(content, style):
    """
    Resolve the cell alignment and explicit style.
    """
    if content.align:
        style = Style(text_align=content.align)

    return style.merge(content.style)


def size_row(row, widths):
    """
    Apply the configured widths to row cells.
    """
    for cell, width in zip(row.cells, widths):
        set_cell_width(cell, width)