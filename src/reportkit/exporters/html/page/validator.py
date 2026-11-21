import re

from .margins import PageMarginRegistry
from .running import RunningElementResolver


class HtmlPageValidator:
    """
    Validate every page setting that ends up in print CSS.
    """

    PAGE_SIZES = {"A4", "A3", "A5", "Letter", "Legal"}
    ORIENTATIONS = {"portrait", "landscape"}
    LENGTH = re.compile(r"^\d+(?:\.\d+)?(?:mm|cm|in|pt)$")

    @classmethod
    def validate(cls, found):
        """
        Validate the collected page components.
        """
        cls.validate_pages(found.pages)
        cls.validate_numbering(found)
        cls.validate_running(found)

    @classmethod
    def validate_pages(cls, pages):
        """
        Pages must share one valid configuration.
        """
        if len({cls.signature(page) for page in pages}) > 1:
            raise ValueError("HTML printing currently requires identical page settings.")
        page = pages[0]
        if page.size not in cls.PAGE_SIZES:
            raise ValueError("Unsupported page size.")
        if page.orientation not in cls.ORIENTATIONS:
            raise ValueError("Unsupported page orientation.")
        if not all(isinstance(value, str) and cls.LENGTH.fullmatch(value) for value in cls.margins(page)):
            raise ValueError("Invalid page margin.")
        if page.page_number_position not in PageMarginRegistry.POSITIONS:
            raise ValueError("Unsupported page number position.")

    @staticmethod
    def validate_numbering(found):
        """
        Only one page numbering definition is supported.
        """
        if len(found.numbers) > 1:
            raise ValueError("Only one page numbering definition is supported.")

    @staticmethod
    def validate_running(found):
        """
        Repeating elements must be unique and must not share the page number margin.
        """
        types = [type(component) for component in found.running]
        if len(types) != len(set(types)):
            raise ValueError("Only one repeating Header and Footer are supported.")
        positions = [RunningElementResolver.position(component) for component in found.running]
        if found.numbers:
            positions.append(found.pages[0].page_number_position)
        if len(positions) != len(set(positions)):
            raise ValueError("Page number position collides with a repeating Header or Footer.")

    @staticmethod
    def margins(page):
        """
        Return the page margins in CSS order.
        """
        return (page.margin_top, page.margin_right, page.margin_bottom, page.margin_left)

    @classmethod
    def signature(cls, page):
        """
        Return the settings that must match across pages.
        """
        return (page.size, page.orientation, page.page_number_position, *cls.margins(page))
