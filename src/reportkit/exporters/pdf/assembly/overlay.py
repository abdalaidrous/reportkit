import json
from collections import defaultdict

from markupsafe import escape

from ...html.direction import text_direction

from ...html.page.components import HtmlPageComponentFinder
from ...html.page.margins import PageMarginRegistry
from ...html.page.numbering import PageNumberStyleResolver
from ...html.page.styles import PageStyleResolver
from ...html.templates import HtmlTemplateEngine
from ..conversion import PdfConversionService


LABEL = "rk-page-number"
STAMP_WIDTH = 2000  # Wider than any page, so a stamped line keeps its alignment whatever the page total's length.

# The overlay is drawn over the report, so nothing but the stamped text may paint.
OVERLAY_CSS = (
    "@page { background: none; } html, body { background: none !important; margin: 0 !important; padding: 0 !important; } "
    ".rk-pdf-page-label { position: relative; height: 0; break-before: page; } .rk-pdf-page-label:first-child { break-before: auto; } "
    ".rk-pdf-page-count { position: absolute; margin: 0; padding: 0; white-space: nowrap; }"
)


class PageOverlay:
    """
    Lay out transparent pages, in the page geometry the report uses, that hold only what needs the merged page total:
    the page numbers in their margin box and every deferred PageCount line in the place its chunk laid it out. They are
    stamped onto the merged chunks once the page count is known.
    """

    BATCH = 500

    def __init__(self, document, context, slots=()):
        """
        Read the page settings and number format; numbering is None when the report has no PageNumber.
        """
        found = HtmlPageComponentFinder.find(document)
        self.context = context
        self.page = found.pages[0] if found.pages else None
        self.numbering = found.numbers[0].format if found.numbers and self.page else None
        self.slots = defaultdict(list)
        for slot in slots:
            self.slots[slot.page].append(slot)
        self.templates = HtmlTemplateEngine()

    @property
    def needed(self):
        """
        Return whether any page needs stamping.
        """
        return bool(self.numbering or self.slots)

    def pdfs(self, total):
        """
        Yield PDFs of up to BATCH overlay pages each, for pages 1 to total.
        """
        for start in range(1, total + 1, self.BATCH):
            numbers = range(start, min(start + self.BATCH, total + 1))
            yield PdfConversionService.convert(self.html(numbers, total))

    def html(self, numbers, total):
        """
        Build one empty page per number, holding its page number label and page count lines.
        """
        labels = "".join(self.label_element(number, total) for number in numbers)
        return self.templates.render("document.html", title="", language=self.context.language, direction=self.context.direction, content=labels, styles=self.styles())

    def styles(self):
        """
        Build the overlay styles using the report's page geometry and page number margin box.
        """
        page = PageStyleResolver.render(self.page, self.margins()) if self.page else ""
        return "\n".join([self.templates.load_styles(), page, OVERLAY_CSS])

    def margins(self):
        """
        Register the page number margin box using the report's numbering position and font declarations.
        """
        margins = PageMarginRegistry()
        if self.numbering:
            margins.register(self.page.page_number_position, f"string({LABEL})", PageNumberStyleResolver.DECLARATIONS)
        return margins.render()

    def label_element(self, number, total):
        """
        Build the element that starts one overlay page: it sets the page number string and holds the page counts.
        """
        numbering = f' style="string-set: {LABEL} {escape(self.label(number, total))}"' if self.numbering else ""
        counts = "".join(self.count_element(slot, total) for slot in self.slots.get(number - 1, ()))
        return f'<div class="rk-pdf-page-label"{numbering}>{counts}</div>'

    def label(self, number, total):
        """
        Return the page number text as a CSS string.
        """
        return json.dumps(self.numbering.replace("{pages}", str(total)).replace("{page}", str(number)), ensure_ascii=False)

    @staticmethod
    def count_element(slot, total):
        """
        Build one page count line at its slot, in the computed style of the line it replaces.
        """
        left = {"left": slot.left, "right": slot.left + slot.width - STAMP_WIDTH}.get(slot.align, slot.left + (slot.width - STAMP_WIDTH) / 2)
        style = (
            f"left: {left:.3f}px; top: {slot.top:.3f}px; width: {STAMP_WIDTH}px; height: {slot.height:.3f}px; line-height: {slot.height:.3f}px; "
            f"font-family: {slot.font_family}; font-size: {slot.font_size}px; font-weight: {slot.font_weight}; color: {slot.color}; "
            f"text-align: {slot.align}; direction: {slot.direction};"
        )
        text = slot.text(total)
        text_dir = text_direction(text)
        text_dir = f' dir="{text_dir}"' if text_dir else ""
        return f'<p class="rk-pdf-page-count" style="{escape(style)}"><span class="rk-page-count__text"{text_dir}>{escape(text)}</span></p>'
