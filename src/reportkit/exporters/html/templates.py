from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


class HtmlTemplateEngine:
    """
    Manage reusable HTML templates and static stylesheets.
    """

    def __init__(self, template_dir=None, static_dir=None):
        """
        Initialize template and stylesheet directories.
        """
        root = Path(__file__).parent
        self.static_dir = Path(static_dir) if static_dir is not None else root / "static"
        self.environment = Environment(
            loader=FileSystemLoader(template_dir or root / "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render(self, template_name: str, **context) -> str:
        """
        Render a template with its context.
        """
        return self.environment.get_template(template_name).render(**context)

    def load_styles(self) -> str:
        """
        Load the default report stylesheets in order.
        """
        files = (
            "tokens.css",
            "base.css",
            "typography.css",
            "layout.css",
            "table.css",
            "print.css",
        )
        return "\n".join(
            (self.static_dir / name).read_text(encoding="utf-8") for name in files
        )
