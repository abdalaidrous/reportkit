class PageMarginRegistry:
    """
    Collect page margin box rules; positions are validated by HtmlPageValidator.
    """

    POSITIONS = {"top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right"}

    def __init__(self):
        """
        Start with no occupied positions.
        """
        self.positions = {}

    def register(self, position, content, declarations=""):
        """
        Register one margin box with optional extra declarations.
        """
        self.positions[position] = (content, declarations)

    def render(self):
        """
        Render the registered margin boxes.
        """
        return [f"@{position} {{ content: {content};{' ' + declarations if declarations else ''} }}" for position, (content, declarations) in self.positions.items()]
