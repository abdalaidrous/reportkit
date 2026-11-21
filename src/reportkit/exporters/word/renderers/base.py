from dataclasses import dataclass, field

from docx.section import _Footer, _Header
from docx.table import _Cell

from ..styles.xml import child, set_attributes

COLLAPSED_LINE = 20


@dataclass
class Area:
    """
    Describe where a renderer writes: a container (document body, table cell, page header or footer) and its width.
    """

    container: object
    width: object
    fresh: bool = field(default=False)

    def paragraph(self):
        """
        Return a new paragraph, reusing the empty one Word puts in every new table cell.
        """
        if self.fresh:
            self.fresh = False
            return self.container.paragraphs[0]
        return self.container.add_paragraph()

    def table(self, rows, columns):
        """
        Add a table; inside a cell the empty paragraphs Word requires around it are removed or collapsed.
        """
        if self.fresh:
            paragraph = self.container.paragraphs[0]._p
            paragraph.getparent().remove(paragraph)
        self.fresh = False
        if isinstance(self.container, (_Header, _Footer)):
            return self.container.add_table(rows, columns, self.width)
        table = self.container.add_table(rows, columns)
        if isinstance(self.container, _Cell):
            collapse(self.container.paragraphs[-1])
        return table

    def cell(self, cell, width):
        """
        Return the area of a table cell.
        """
        return Area(cell, width, fresh=True)


def collapse(paragraph):
    """
    Shrink the closing paragraph Word requires after a table in a cell to almost nothing.
    """
    set_attributes(child(paragraph._p.get_or_add_pPr(), "w:spacing"), before=0, after=0, line=COLLAPSED_LINE, lineRule="exact")
