from ...components.document import Page
from ...components.pagination import PageNumber
from .page_margins import PageMarginRenderer
from .pagination import PageNumberStyleResolver
from .page_styles import PageStyleResolver


class HtmlPageResolver:
    """Resolve print settings from a report document."""

    @classmethod
    def resolve(cls, document):
        """Return the stylesheet for the report page."""
        pages = cls.find_pages(document)
        if not pages:
            return ""
        settings = {cls.signature(page) for page in pages}
        if len(settings) > 1:
            raise ValueError("HTML printing currently requires identical page settings.")
        numbers = cls.find_page_numbers(document)
        if len(numbers) > 1:
            raise ValueError("Only one page numbering definition is supported.")
        rules = []
        if numbers:
            content = PageNumberStyleResolver.resolve(numbers[0].format)
            rules.append(PageMarginRenderer.render(pages[0].page_number_position, content))
        return PageStyleResolver.render(pages[0], rules)

    @classmethod
    def find_pages(cls, component):
        """Find page components recursively."""
        pages = []
        if isinstance(component, Page):
            pages.append(component)
        for child in getattr(component, "children", []):
            pages.extend(cls.find_pages(child))
        return pages

    @staticmethod
    def signature(page):
        """Return the page print configuration."""
        return (
            page.size,
            page.orientation,
            page.margin_top,
            page.margin_right,
            page.margin_bottom,
            page.margin_left,
        )

    @classmethod
    def find_page_numbers(cls, component):
        """Find page numbering definitions recursively."""
        numbers = []
        if isinstance(component, PageNumber):
            numbers.append(component)
        for child in getattr(component, "children", []):
            numbers.extend(cls.find_page_numbers(child))
        return numbers
