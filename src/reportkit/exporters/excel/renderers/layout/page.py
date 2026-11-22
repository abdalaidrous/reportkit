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


class PageCountRenderer:
    """
    Render the page total in the printed footer: cells have no pages, so only the print footer can show it.
    """

    def render(self, component, context, engine, region):
        """
        Put the page count format in the right footer section, beside the centred page number; it takes no rows.
        """
        engine.sheet.set_footer(component.format, "right")
        return 0
