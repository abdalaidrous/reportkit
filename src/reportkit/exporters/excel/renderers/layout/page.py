class PageBreakRenderer:
    """
    Render a page break as an Excel row break.
    """

    def render(self, component, context, engine, region):
        """
        Break the printed page before the region row.
        """
        engine.sheet.add_page_break(region.row - 1)
        return 0


class PageNumberRenderer:
    """
    Render page numbering in the printed footer.
    """

    def render(self, component, context, engine, region):
        """
        Put the page number format in the footer; it takes no rows.
        """
        engine.sheet.set_footer(component.format)
        return 0
