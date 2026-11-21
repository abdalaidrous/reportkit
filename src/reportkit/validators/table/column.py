import re

ALIGNMENTS = {"start", "center", "end", "left", "right"}
VERTICAL_ALIGNMENTS = {"top", "middle", "bottom"}
FORMATS = {None, "text", "number", "currency", "percent", "date", "datetime"}
WIDTH = re.compile(r"^\d+(?:\.\d+)?(?:px|%|mm|cm|in|pt|em|rem)$")


class TableColumnValidator:
    """
    Validate TableColumn definitions.
    """

    @classmethod
    def validate(cls, column):
        """
        Run every column rule.
        """
        cls.validate_identity(column)
        cls.validate_presentation(column)
        cls.validate_formatting(column)

    @staticmethod
    def validate_identity(column):
        """
        Validate the key and the header texts.
        """
        if not isinstance(column.key, str) or not column.key:
            raise ValueError("Column key must be a non-empty string.")
        if not isinstance(column.title, str):
            raise TypeError("Column title must be a string.")
        if column.subtitle is not None and not isinstance(column.subtitle, str):
            raise TypeError("Column subtitle must be a string.")

    @staticmethod
    def validate_presentation(column):
        """
        Validate alignment, width and wrapping.
        """
        if column.align not in ALIGNMENTS:
            raise ValueError("Invalid column alignment.")
        if column.header_align is not None and column.header_align not in ALIGNMENTS:
            raise ValueError("Invalid column header alignment.")
        if column.vertical_align not in VERTICAL_ALIGNMENTS:
            raise ValueError("Invalid column vertical alignment.")
        if column.width is not None and (not isinstance(column.width, str) or not WIDTH.fullmatch(column.width)):
            raise ValueError("Column width must be a CSS length such as '20%' or '30mm'.")
        if not isinstance(column.nowrap, bool):
            raise TypeError("Column nowrap must be a boolean.")

    @staticmethod
    def validate_formatting(column):
        """
        Validate value formatting options.
        """
        if column.format not in FORMATS:
            raise ValueError("Invalid column format.")
        if not isinstance(column.decimals, int) or isinstance(column.decimals, bool) or not 0 <= column.decimals <= 12:
            raise ValueError("Decimals must be an integer between 0 and 12.")
        for name in ("currency", "date_format"):
            if getattr(column, name) is not None and not isinstance(getattr(column, name), str):
                raise TypeError(f"Column {name} must be a string.")
