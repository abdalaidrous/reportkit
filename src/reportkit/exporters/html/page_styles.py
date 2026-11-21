import re


class PageStyleResolver:
    """Resolve page settings into print CSS."""

    LENGTH_PATTERN = re.compile(r"^\d+(?:\.\d+)?(?:mm|cm|in|pt)$")
    PAGE_SIZES = {"A4", "A3", "A5", "Letter", "Legal"}

    @classmethod
    def resolve(cls, page):
        """Build the page print stylesheet."""
        if page.size not in cls.PAGE_SIZES:
            raise ValueError("Unsupported page size.")
        if page.orientation not in {"portrait", "landscape"}:
            raise ValueError("Unsupported page orientation.")
        margins = [page.margin_top, page.margin_right, page.margin_bottom, page.margin_left]
        if not all(isinstance(value, str) and cls.LENGTH_PATTERN.fullmatch(value) for value in margins):
            raise ValueError("Invalid page margin.")
        return (
            "@page {\n"
            f"    size: {page.size} {page.orientation};\n"
            f"    margin: {page.margin_top} {page.margin_right} {page.margin_bottom} {page.margin_left};\n"
            "}"
        )

    @classmethod
    def render(cls, page, margin_rules=None):
        """Build page CSS with optional margin content."""
        base_css = cls.resolve(page)
        if not margin_rules:
            return base_css
        rules = "\n".join(margin_rules)
        index = base_css.rfind("}")
        return base_css[:index] + rules + "\n" + base_css[index:]
