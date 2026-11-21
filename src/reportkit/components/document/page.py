from dataclasses import dataclass

from ...core.container import Container


@dataclass(kw_only=True)
class Page(Container):
    """
    Define a report page and its print settings; the HTML exporter validates them in HtmlPageValidator.
    """

    size: str = "A4"
    orientation: str = "portrait"
    margin_top: str = "15mm"
    margin_right: str = "15mm"
    margin_bottom: str = "15mm"
    margin_left: str = "15mm"
    page_number_position: str = "bottom-right"
