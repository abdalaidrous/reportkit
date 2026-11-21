from ...core.component import Component
from .column import ALIGNMENTS


class TableCellValidator:
    """
    Validate TableCell definitions.
    """

    @classmethod
    def validate(cls, cell):
        """
        Run every cell rule.
        """
        cls.validate_content(cell)
        cls.validate_presentation(cell)

    @staticmethod
    def validate_content(cell):
        """
        A cell shows either a plain value or child components, never both.
        """
        if not isinstance(cell.children, (list, tuple)) or not all(isinstance(child, Component) for child in cell.children):
            raise TypeError("Table cell children must be Component instances.")
        if cell.children and cell.value is not None:
            raise ValueError("TableCell accepts either value or children, not both.")

    @staticmethod
    def validate_presentation(cell):
        """
        Validate alignment and spans.
        """
        if cell.align is not None and cell.align not in ALIGNMENTS:
            raise ValueError("Invalid cell alignment.")
        for name in ("colspan", "rowspan"):
            span = getattr(cell, name)
            if not isinstance(span, int) or isinstance(span, bool) or span < 1:
                raise ValueError(f"Table cell {name} must be a positive integer.")
