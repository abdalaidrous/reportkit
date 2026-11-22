PAGES = "{pages}"


class PageCountValidator:
    """
    Validate PageCount definitions.
    """

    @staticmethod
    def validate(count):
        """
        The format is text around exactly one {pages} placeholder, without the current page.
        """
        if not isinstance(count.format, str):
            raise TypeError("Page count format must be a string.")
        if count.format.count(PAGES) != 1:
            raise ValueError("Page count format must contain {pages} exactly once.")
        if "{page}" in count.format:
            raise ValueError("Page count format cannot show the current page; use PageNumber for {page}.")
