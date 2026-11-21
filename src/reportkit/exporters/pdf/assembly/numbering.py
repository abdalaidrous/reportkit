import json

from markupsafe import escape

from ...html.page.components import HtmlPageComponentFinder
from ...html.page.margins import PageMarginRegistry
from ...html.page.numbering import PageNumberStyleResolver
from ...html.page.styles import PageStyleResolver
from ...html.templates import HtmlTemplateEngine
from ..conversion import PdfConversionService


LABEL = "rk-page-number"

# The overlay is drawn over the report, so nothing but the numbers may paint.
LABEL_CSS = "@page { background: none; } html, body { background: none !important; } .rk-pdf-page-label { break-before: page; } .rk-pdf-page-label:first-child { break-before: auto; }"


class PageNumberOverlay:
    """
    Lay out transparent pages that hold only the page numbers, in the margin box, font and page geometry the report
    uses, to be stamped onto the merged chunks once the page count is known.
    """

    BATCH = 500

    def __init__(self, document, context):
        """
        Read the page settings and number format; numbering is None when the report has no PageNumber.
        """
        found = HtmlPageComponentFinder.find(document)
        self.context = context
        self.page = found.pages[0] if found.pages else None
        self.numbering = found.numbers[0].format if found.numbers and self.page else None
        self.templates = HtmlTemplateEngine()

    def pdfs(self, total):
        """
        Yield PDFs of up to BATCH numbered pages each, for pages 1 to total.
        """
        for start in range(1, total + 1, self.BATCH):
            numbers = range(start, min(start + self.BATCH, total + 1))
            yield PdfConversionService.convert(self.html(numbers, total))

    def html(self, numbers, total):
        """
        Build one empty page per number, each naming its own label for the page number margin box.
        """
        styles = self.styles()
        labels = self.labels(numbers, total)
        return self.templates.render("document.html", title="", language=self.context.language, direction=self.context.direction, content=labels, styles=styles)

    def styles(self):
        """
        Build the overlay styles using the report's page geometry and page number margin box.
        """
        margins = self.margins()
        return "\n".join([self.templates.load_styles(), PageStyleResolver.render(self.page, margins), LABEL_CSS])

    def margins(self):
        """
        Register the page number margin box using the report's numbering position and font declarations.
        """
        margins = PageMarginRegistry()
        margins.register(self.page.page_number_position, f"string({LABEL})", PageNumberStyleResolver.DECLARATIONS)
        return margins.render()

    def labels(self, numbers, total):
        """
        Build one transparent page label element for each page number in the batch.
        """
        return "".join(self.label_element(number, total) for number in numbers)

    def label_element(self, number, total):
        """
        Build the HTML element that sets the page number string for its margin box.
        """
        return f'<div class="rk-pdf-page-label" style="string-set: {LABEL} {escape(self.label(number, total))}"></div>'

    def label(self, number, total):
        """
        Return the page number text as a CSS string.
        """
        return json.dumps(self.numbering.replace("{pages}", str(total)).replace("{page}", str(number)), ensure_ascii=False)