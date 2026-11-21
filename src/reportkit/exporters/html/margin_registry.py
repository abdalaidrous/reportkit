class PageMarginRegistry:
    """Manage occupied page margin positions."""

    def __init__(self):
        self.positions = {}

    def register(self, position, content):
        """Register one page margin rule."""
        if position in self.positions:
            raise ValueError(f"Page margin position '{position}' is already occupied.")
        self.positions[position] = content

    def render(self):
        """Render registered margin rules."""
        return [f"@{position} {{ content: {content}; }}" for position, content in self.positions.items()]
