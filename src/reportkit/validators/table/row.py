from collections.abc import Mapping

ROW_KINDS = {"data", "group-header", "subtotal", "total"}


class TableRowValidator:
    """
    Validate TableRow definitions.
    """

    @classmethod
    def validate(cls, row):
        """
        Run every row rule.
        """
        cls.validate_kind(row)
        cls.validate_content(row)

    @staticmethod
    def validate_kind(row):
        """
        Validate the row kind.
        """
        if row.kind not in ROW_KINDS:
            raise ValueError("Unsupported table row kind.")

    @staticmethod
    def validate_content(row):
        """
        Validate values and explicit cells.
        """
        from ...components.table.cell import TableCell  # Deferred: the component modules import this validator.

        if not isinstance(row.values, Mapping):
            raise TypeError("Table row values must be a mapping.")
        if row.cells is not None and not all(isinstance(cell, TableCell) for cell in row.cells):
            raise TypeError("Row cells must contain TableCell instances.")
