class PageMarginRegistry:
    """Manage occupied page margin positions."""

    def __init__(self):
        self.positions = {}

    def register(self, position, content, declarations=""):
        """Register one page margin rule with optional extra CSS declarations."""
        if position in self.positions:
            raise ValueError(f"Page margin position '{position}' is already occupied.")
        self.positions[position] = (content, declarations)

    def render(self):
        """Render registered margin rules."""
        return [
            f"@{position} {{ content: {content};{' ' + declarations if declarations else ''} }}"
            for position, (content, declarations) in self.positions.items()
        ]
