import reportkit.exporters.html  # noqa: F401  (registers the HTML renderers)
from reportkit.components.document import Report
from reportkit.exporters.html.exporter import HtmlExporter
from reportkit.rendering.context import RenderingContext


def export_html(*children, direction="rtl"):
    """
    Export a report with the given children and return the HTML text.
    """
    report = Report(title="Test", children=list(children))
    return HtmlExporter().export(report, RenderingContext(language="ar", direction=direction)).decode("utf-8")
