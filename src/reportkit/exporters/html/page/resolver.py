from .components import HtmlPageComponentFinder
from .margins import PageMarginRegistry
from .numbering import PageNumberStyleResolver
from .running import RunningElementResolver
from .styles import PageStyleResolver
from .validator import HtmlPageValidator


class HtmlPageResolver:
    """
    Coordinate building the print CSS of a report.
    """

    @classmethod
    def resolve(cls, document, numbering=True):
        """
        Return the print stylesheet for the report pages; numbering=False leaves the page number out of the margins.
        """
        found = HtmlPageComponentFinder.find(document)

        if not found.pages:
            return ""

        HtmlPageValidator.validate(found)
        return cls.build(found, numbering)

    @classmethod
    def build(cls, found, numbering):
        """
        Build the page stylesheet and append the running element styles when available.
        """
        page = found.pages[0]
        margins = cls.margins(page, found, numbering)
        running_css = RunningElementResolver.resolve(found.running)
        return PageStyleResolver.render(page, margins.render()) + ("\n" + running_css if running_css else "")

    @classmethod
    def margins(cls, page, found, numbering=True):
        """
        Register the page number and running elements in the page margins.
        """
        margins = PageMarginRegistry()
        cls.register_number(margins, page, found, numbering)
        cls.register_running(margins, found.running)
        return margins

    @staticmethod
    def register_number(margins, page, found, numbering):
        """
        Register the page number margin box when page numbering is enabled and configured.
        """
        if numbering and found.numbers:
            margins.register(page.page_number_position, PageNumberStyleResolver.resolve(found.numbers[0].format), PageNumberStyleResolver.DECLARATIONS)

    @staticmethod
    def register_running(margins, components):
        """
        Register running headers and footers in their configured page margin boxes.
        """
        for component in components:
            margins.register(RunningElementResolver.position(component), f"element({RunningElementResolver.name(component)})")