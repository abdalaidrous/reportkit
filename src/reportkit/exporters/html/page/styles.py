class PageStyleResolver:
    """
    Build the @page rule; settings are validated by HtmlPageValidator.
    """

    @staticmethod
    def resolve(page):
        """
        Build the base @page rule.
        """
        return f"@page {{\n    size: {page.size} {page.orientation};\n    margin: {page.margin_top} {page.margin_right} {page.margin_bottom} {page.margin_left};\n}}"

    @classmethod
    def render(cls, page, margin_rules=None):
        """
        Build the @page rule with its margin boxes.
        """
        base_css = cls.resolve(page)
        if not margin_rules:
            return base_css
        index = base_css.rfind("}")
        return base_css[:index] + "\n".join(margin_rules) + "\n" + base_css[index:]
