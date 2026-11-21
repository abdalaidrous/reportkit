from docx.shared import Pt

from ....components.document import Page
from ..renderers import WORD_RENDERERS
from ..renderers.base import Area
from ..styles.text import points
from ..styles.xml import child, set_attributes
from .document import WordDocument


class WordEngine:
    """
    Walk the component tree and write it into a Word document, one renderer per component type.
    """

    def __init__(self, document, context):
        """
        Create the Word document sized to the first page of the report.
        """
        page = next(find_components(document, Page), None)
        self.word, self.direction = WordDocument(document.title, page), context.direction
        self.page_number_position = page.page_number_position if page else "bottom-right"
        self.header_area = Area(self.word.section.header, self.word.content_width, fresh=True)
        self.footer_area = Area(self.word.section.footer, self.word.content_width, fresh=True)

    def write(self, document, context, target):
        """
        Render the report into the document body and write the DOCX to a file path or a binary stream.
        """
        try:
            self.render(document, context, Area(self.word.document, self.word.content_width))
        except BaseException:
            self.word.spool.close()
            raise
        self.word.save(target)

    @property
    def spool(self):
        """
        Return the spool that keeps finished table rows out of memory.
        """
        return self.word.spool

    def render(self, component, context, area):
        """
        Render one component with its vertical margins.
        """
        style = context.resolve_style(component)
        self.add_gap(area, style.margin_top)
        WORD_RENDERERS.get(component).render(component, context, self, area)
        self.add_gap(area, style.margin_bottom)

    def add_gap(self, area, margin):
        """
        Turn a vertical CSS margin into an empty paragraph of the same height.
        """
        if margin and points(margin) >= 3:
            paragraph = area.paragraph()
            paragraph.paragraph_format.space_before, paragraph.paragraph_format.space_after = Pt(0), Pt(0)
            set_attributes(child(paragraph._p.get_or_add_pPr(), "w:spacing"), line=round(points(margin) * 20), lineRule="exact")

    def header(self):
        """
        Return the page header area repeated on every page.
        """
        return self.header_area

    def footer(self):
        """
        Return the page footer area repeated on every page.
        """
        return self.footer_area


def find_components(component, kind):
    """
    Yield the components of one type in the tree without touching table rows.
    """
    if isinstance(component, kind):
        yield component
    for child_component in getattr(component, "children", []):
        yield from find_components(child_component, kind)
