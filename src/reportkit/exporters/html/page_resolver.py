from ...components.document import Page
from ...components.pagination import PageNumber
from .page_margins import PageMarginRenderer
from .margin_registry import PageMarginRegistry
from .pagination import PageNumberStyleResolver
from .running_elements import RunningElementResolver
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
        margins = PageMarginRegistry()
        if numbers:
            content = PageNumberStyleResolver.resolve(numbers[0].format)
            margins.register(pages[0].page_number_position, content)
        running = RunningElementResolver.find_components(document)
        RunningElementResolver.validate(running)
        for component in running:
            name, position = RunningElementResolver.ELEMENTS[type(component)]
            margins.register(position, f"element({name})")
        page_css = PageStyleResolver.render(pages[0], margins.render())
        running_css = RunningElementResolver.resolve(document)
        return page_css + ("\n" + running_css if running_css else "")

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
