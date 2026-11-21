from .components import HtmlPageComponentFinder
from .margins import PageMarginRegistry
from .numbering import PageNumberStyleResolver
from .running import RunningElementResolver
from .styles import PageStyleResolver
from .validator import HtmlPageValidator


class HtmlPageResolver:
    """Coordinate building the print CSS of a report."""

    @classmethod
    def resolve(cls, document):
        """Return the print stylesheet for the report pages."""
        found = HtmlPageComponentFinder.find(document)
        if not found.pages:
            return ""
        HtmlPageValidator.validate(found)
        page = found.pages[0]
        running_css = RunningElementResolver.resolve(found.running)
        return PageStyleResolver.render(page, cls.margins(page, found).render()) + ("\n" + running_css if running_css else "")

    @staticmethod
    def margins(page, found):
        """Register the page number and running elements in the page margins."""
        margins = PageMarginRegistry()
        if found.numbers:
            margins.register(page.page_number_position, PageNumberStyleResolver.resolve(found.numbers[0].format), PageNumberStyleResolver.DECLARATIONS)
        for component in found.running:
            margins.register(RunningElementResolver.position(component), f"element({RunningElementResolver.name(component)})")
        return margins
