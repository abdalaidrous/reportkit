import re

from .....styles.style import Style
from ...styles.text import add_page_break, add_run, format_paragraph
from ...styles.xml import add_field


PAGE_FIELDS = {"{page}": "PAGE", "{pages}": "NUMPAGES"}
PAGE_PATTERN = re.compile(r"(\{page\}|\{pages\})")
PAGE_FONT_SIZE = 11
PAGE_COLOR = "#555555"


class PageBreakRenderer:
    """
    Render a page break.
    """

    def render(self, component, context, engine, area):
        """
        Start a new page.
        """
        add_page_break(area.paragraph())


class PageNumberRenderer:
    """
    Render page numbering using Word PAGE and NUMPAGES fields.
    """

    def render(self, component, context, engine, area):
        """
        Render the page number in the configured header or footer.
        """
        position = engine.page_number_position
        paragraph = self.get_paragraph(engine, position)
        style = self.get_style(position)

        format_paragraph(paragraph, style, "ltr")
        self.render_parts(paragraph, component.format, style)

    @staticmethod
    def get_paragraph(engine, position):
        """
        Return the page header or footer paragraph.
        """
        area = engine.header() if position.startswith("top") else engine.footer()
        return area.paragraph()

    @staticmethod
    def get_style(position):
        """
        Resolve the page number style and alignment.
        """
        return Style(text_align=position.split("-")[1], font_size=PAGE_FONT_SIZE, color=PAGE_COLOR)

    @classmethod
    def render_parts(cls, paragraph, format_text, style):
        """
        Render page number fields and static text.
        """
        for part in PAGE_PATTERN.split(format_text):
            cls.render_part(paragraph, part, style)

    @staticmethod
    def render_part(paragraph, part, style):
        """
        Render a Word field or a text run.
        """
        if part in PAGE_FIELDS:
            add_field(paragraph, PAGE_FIELDS[part])
        elif part:
            add_run(paragraph, part, style, "ltr")