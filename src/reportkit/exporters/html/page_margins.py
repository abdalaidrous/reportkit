class PageMarginRenderer:
    """Build page margin rules for print rendering."""

    POSITIONS = {
        "top-left": "@top-left",
        "top-center": "@top-center",
        "top-right": "@top-right",
        "bottom-left": "@bottom-left",
        "bottom-center": "@bottom-center",
        "bottom-right": "@bottom-right",
    }

    @classmethod
    def render(cls, position, content):
        """Build one CSS page margin rule."""
        if position not in cls.POSITIONS:
            raise ValueError("Unsupported page margin position.")
        return f"{cls.POSITIONS[position]} {{ content: {content}; }}"
