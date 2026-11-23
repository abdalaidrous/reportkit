from collections.abc import Iterable


class TableValidator:
    """
    Validate Table configuration; rows stay lazy and are checked as they are rendered.
    """

    @classmethod
    def validate(cls, table):
        """
        Run every table rule that does not consume the rows.
        """
        cls.validate_columns(table.columns)
        cls.validate_rows(table)
        cls.validate_style(table.table_style)

    @staticmethod
    def validate_columns(columns):
        """
        Validate column types and unique keys.
        """
        from ...components.table.column import TableColumn

        if not columns:
            raise ValueError("Table must contain at least one column.")

        if not all(isinstance(column, TableColumn) for column in columns):
            raise TypeError("All columns must be TableColumn instances.")

        keys = [column.key for column in columns]
        if len(keys) != len(set(keys)):
            raise ValueError("Table column keys must be unique.")

    @classmethod
    def validate_rows(cls, table):
        """
        Validate the rows container and the footer.
        """
        if not isinstance(table.rows, Iterable):
            raise TypeError("Table rows must be iterable.")

        if table.footer is not None:
            cls.validate_row(table.footer)

    @staticmethod
    def validate_row(row):
        """
        Validate one row as it is consumed.
        """
        from ...components.table.row import TableRow

        if not isinstance(row, TableRow):
            raise TypeError("Table rows must be TableRow instances.")

    @staticmethod
    def validate_style(table_style):
        """
        Validate the table presentation settings.
        """
        from ...components.table.style import TableStyle
        from ...styles.style import Style

        if not isinstance(table_style, TableStyle):
            raise TypeError("Table style must be a TableStyle instance.")

        if table_style.layout not in ("fixed", "auto"):
            raise ValueError("Table layout must be 'fixed' or 'auto'.")

        if table_style.header_style is not None and not isinstance(table_style.header_style, Style):
            raise TypeError("Table header_style must be a Style instance.")