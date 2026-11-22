from .....rendering.qr import QRCodeImage
from ..base import BaseHtmlRenderer


class QRCodeRenderer(BaseHtmlRenderer):
    """
    Render a QR code as an embedded SVG image, sharp at any zoom and in print.
    """

    template_name = "components/media/qr_code.html"

    def render(self, component, context, engine):
        """
        Render the QR code at its declared size.
        """
        style = engine.styles.resolve(context.resolve_style(component))
        source = QRCodeImage(component).svg_data_uri()
        return engine.templates.render(self.template_name, component=component, source=source, style=style)
