class PageNumberValidator:
    """
    Validate PageNumber definitions.
    """

    @staticmethod
    def validate(number):
        """
        The format is a non-empty string; {page} and {pages} are optional.
        """
        if not isinstance(number.format, str):
            raise TypeError("Page number format must be a string.")
        if not number.format:
            raise ValueError("Page number format cannot be empty.")
