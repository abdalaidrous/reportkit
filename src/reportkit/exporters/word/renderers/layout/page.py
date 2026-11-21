import re

from .....styles.style import Style
from ...styles.text import add_page_break, add_run, format_paragraph
from ...styles.xml import add_field

PAGE_FIELDS = {"{page}": "PAGE", "{pages}": "NUMPAGES"}


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
    Render page numbering in the Word page header or footer with PAGE and NUMPAGES fields.
    """

    def render(self, component, context, engine, area):
        """
        Write the page number format at the Page component's position.
        """
        position = engine.page_number_position
        paragraph = (engine.header() if position.startswith("top") else engine.footer()).paragraph()
        format_paragraph(paragraph, Style(text_align=position.split("-")[1], font_size=11, color="#555555"), "ltr")
        for part in re.split(r"(\{page\}|\{pages\})", component.format):
            if part in PAGE_FIELDS:
                add_field(paragraph, PAGE_FIELDS[part])
            else:
                add_run(paragraph, part, Style(font_size=11, color="#555555"), "ltr")
