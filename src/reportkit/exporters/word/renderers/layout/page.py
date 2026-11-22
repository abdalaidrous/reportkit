import re

from .....styles.style import Style
from ...styles.text import add_page_break, add_run, format_paragraph
from ...styles.xml import add_field


PAGE_FIELDS = {"{page}": "PAGE", "{pages}": "NUMPAGES"}
PAGE_PATTERN = re.compile(r"(\{page\}|\{pages\})")
PAGE_FONT_SIZE = 11
PAGE_COLOR = "#555555"


def render_page_part(paragraph, part, style, direction="ltr"):
    """
    Render a Word page field or a static text run.
    """
    if part in PAGE_FIELDS:
        add_field(paragraph, PAGE_FIELDS[part])
    elif part:
        add_run(paragraph, part, style, direction)


def render_page_format(paragraph, format_text, style, direction="ltr"):
    """
    Render formatted page numbering by splitting static text and Word fields.
    """
    for part in PAGE_PATTERN.split(format_text):
        render_page_part(paragraph, part, style, direction)


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
        render_page_format(paragraph, component.format, style)

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


class PageCountRenderer:
    """
    Render the page total as a paragraph with a Word NUMPAGES field, in the body or a header or footer.
    """

    def render(self, component, context, engine, area):
        """
        Write the text around the page total in the component style.
        """
        style = context.resolve_style(component)
        paragraph = area.paragraph()
        before, after = component.parts

        format_paragraph(paragraph, style, engine.direction)
        render_page_part(paragraph, before, style)
        add_field(paragraph, PAGE_FIELDS["{pages}"])
        render_page_part(paragraph, after, style)
