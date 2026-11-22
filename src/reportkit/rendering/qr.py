import math
from io import BytesIO

import segno


class QRCodeImage:
    """
    Encode a QRCode component as the image each exporter embeds: SVG for HTML/PDF, PNG for Excel and Word.
    """

    def __init__(self, component):
        """
        Encode the value at the declared error correction level, never raised silently.
        """
        self.component = component
        self.symbol = segno.make(component.value, error=component.error_correction.lower(), micro=False, boost_error=False)

    def svg_data_uri(self):
        """
        Return a scalable SVG data URI; its size comes from the element that shows it.
        """
        return self.symbol.svg_data_uri(scale=1, border=self.component.quiet_zone, omitsize=True)

    def png(self):
        """
        Return PNG bytes with whole pixels per module, at least the declared size.
        """
        modules = self.symbol.symbol_size(scale=1, border=self.component.quiet_zone)[0]
        buffer = BytesIO()
        self.symbol.save(buffer, kind="png", scale=max(1, math.ceil(self.component.size / modules)), border=self.component.quiet_zone)
        buffer.seek(0)
        return buffer
