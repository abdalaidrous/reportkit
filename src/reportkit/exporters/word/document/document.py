from io import BytesIO

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.shared import Mm, Pt

from ....styles.tokens import token
from ..exceptions import WordExportError
from ..styles.text import DEFAULT_FONT, points
from .package import DocxPackage
from .spool import RowSpool

PAPER_MILLIMETRES = {"A3": (297, 420), "A4": (210, 297), "A5": (148, 210), "Letter": (216, 279), "Legal": (216, 356)}


class WordDocument:
    """
    Own the python-docx document: page size, orientation and margins, default font, the spool of finished table rows,
    and saving.
    """

    def __init__(self, title, page):
        """
        Create the document and apply the first Page component settings (A4 portrait, 15 mm margins otherwise).
        """
        self.document = Document()
        self.document.core_properties.title = title or ""
        self.section = self.document.sections[0]
        self.spool = RowSpool()
        self.set_page(page)
        self.set_default_font()

    @property
    def content_width(self):
        """
        Return the width between the page margins.
        """
        return self.section.page_width - self.section.left_margin - self.section.right_margin

    def set_page(self, page):
        """
        Apply paper size, orientation and margins.
        """
        width, height = PAPER_MILLIMETRES.get(page.size if page else "A4", PAPER_MILLIMETRES["A4"])
        landscape = bool(page) and page.orientation == "landscape"
        self.section.orientation = WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
        self.section.page_width, self.section.page_height = (Mm(height), Mm(width)) if landscape else (Mm(width), Mm(height))
        margins = (page.margin_top, page.margin_right, page.margin_bottom, page.margin_left) if page else ("15mm",) * 4
        self.section.top_margin, self.section.right_margin, self.section.bottom_margin, self.section.left_margin = (length(value) for value in margins)

    def set_default_font(self):
        """
        Use the report font and body size for the Normal style.
        """
        normal = self.document.styles["Normal"]
        normal.font.name, normal.font.size = DEFAULT_FONT, Pt(points(token("--rk-font-md")))
        normal.paragraph_format.space_after = Pt(0)

    def save(self, target):
        """
        Write the DOCX to a file path or a binary stream, splicing the spooled table rows back in.
        """
        try:
            if not self.spool.segments:
                return self.document.save(target)
            buffer = BytesIO()
            self.document.save(buffer)
            DocxPackage.write(buffer.getvalue(), self.spool, target)
        except (OSError, ValueError, TypeError) as error:
            raise WordExportError(f"Could not write the DOCX file: {error}") from error
        finally:
            self.spool.close()


def length(value):
    """
    Convert a CSS length such as "12mm" into a Word length.
    """
    factor = {"mm": 1, "cm": 10, "in": 25.4, "pt": 25.4 / 72}.get(str(value)[-2:])
    if factor is None:
        raise WordExportError(f"Page margin {value!r} must use mm, cm, in or pt.")
    return Mm(float(value[:-2]) * factor)
