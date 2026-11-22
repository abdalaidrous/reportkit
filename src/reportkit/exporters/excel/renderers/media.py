import base64
import binascii
import math
from io import BytesIO

from ....rendering.qr import QRCodeImage
from ...html.assets import AssetResolver
from ..exceptions import ExcelExportError

ROW_HEIGHT_PIXELS = 20
EXCEL_IMAGE_TYPES = ("image/png", "image/jpeg", "image/gif", "image/bmp")


class ImageRenderer:
    """
    Render an Image anchored at the region's first cell; local files are embedded through AssetResolver.
    """

    def render(self, component, context, engine, region):
        """
        Place the image and return the rows it covers.
        """
        height = engine.sheet.add_image(self.get_data(component), region.row, region.column, region.width, pixels(component.width), pixels(component.height))
        return max(1, math.ceil(height / ROW_HEIGHT_PIXELS))

    @staticmethod
    def get_data(component):
        """
        Decode the image into bytes Excel can embed (PNG, JPEG, GIF or BMP).
        """
        uri = AssetResolver.resolve(component.src)
        if not uri.startswith("data:"):
            raise ExcelExportError(f"Excel export embeds local images only; remote image refused: {component.src}")
        mime, _, payload = uri[len("data:"):].partition(";base64,")
        if mime not in EXCEL_IMAGE_TYPES:
            raise ExcelExportError(f"Excel cannot embed {mime} images ({component.src}); use PNG or JPEG.")
        try:
            return BytesIO(base64.b64decode(payload, validate=True))
        except binascii.Error as error:
            raise ExcelExportError(f"Image data is not valid base64: {component.src}") from error


class QRCodeRenderer:
    """
    Render a QR code as a PNG image anchored at the region's first cell.
    """

    def render(self, component, context, engine, region):
        """
        Place the QR code at its declared size and return the rows it covers.
        """
        height = engine.sheet.add_image(QRCodeImage(component).png(), region.row, region.column, region.width, component.size, component.size)
        return max(1, math.ceil(height / ROW_HEIGHT_PIXELS))


def pixels(value):
    """
    Read a pixel size such as "76" or "76px", or None.
    """
    return int(value.removesuffix("px")) if value and value.removesuffix("px").isdigit() else None
