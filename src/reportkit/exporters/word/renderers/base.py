from dataclasses import dataclass, field

from docx.section import _Footer, _Header
from docx.table import _Cell

from ..styles.xml import child, set_attributes


COLLAPSED_LINE = 20


@dataclass
class Area:
    """
    Manage the rendering area for document bodies, cells, headers, and footers.
    """

    container: object
    width: object
    fresh: bool = field(default=False)

    def paragraph(self):
        """
        Create a paragraph or reuse the initial empty cell paragraph.
        """
        if self.fresh:
            self.fresh = False
            return self.container.paragraphs[0]

        return self.container.add_paragraph()

    def table(self, rows, columns):
        """
        Create a table and manage surrounding cell paragraphs.
        """
        self.remove_initial_paragraph()
        table = self.create_table(rows, columns)
        self.collapse_cell_paragraph()
        return table

    def remove_initial_paragraph(self):
        """
        Remove the initial empty paragraph when the area is fresh.
        """
        if not self.fresh:
            return

        paragraph = self.container.paragraphs[0]._p
        paragraph.getparent().remove(paragraph)
        self.fresh = False

    def create_table(self, rows, columns):
        """
        Create a table with the required container arguments.
        """
        if isinstance(self.container, (_Header, _Footer)):
            return self.container.add_table(rows, columns, self.width)

        return self.container.add_table(rows, columns)

    def collapse_cell_paragraph(self):
        """
        Collapse the closing paragraph after a table inside a cell.
        """
        if isinstance(self.container, _Cell):
            collapse(self.container.paragraphs[-1])

    @staticmethod
    def cell(cell, width):
        """
        Create a rendering area for a table cell.
        """
        return Area(cell, width, fresh=True)


def collapse(paragraph):
    """
    Collapse the required closing paragraph after a table.
    """
    spacing = child(paragraph._p.get_or_add_pPr(), "w:spacing")
    set_attributes(spacing, before=0, after=0, line=COLLAPSED_LINE, lineRule="exact")