import base64
import binascii
from io import BytesIO

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Emu

from ....rendering.qr import QRCodeImage
from ...html.assets import AssetResolver
from ..exceptions import WordExportError


WORD_IMAGE_TYPES = ("image/png", "image/jpeg", "image/gif", "image/bmp")
EMU_PER_PIXEL = 9525


def add_picture(area, data, width=None, height=None):
    """
    Add a centered picture to a Word paragraph using the supplied dimensions.
    """
    paragraph = area.paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(data, width=width, height=height)


def emu(value):
    """
    Convert a pixel size such as "76" or "76px" into a Word length, or None.
    """
    return Emu(int(value.removesuffix("px")) * EMU_PER_PIXEL) if value and value.removesuffix("px").isdigit() else None


class ImageRenderer:
    """
    Render an Image centred in its area; local files are embedded through AssetResolver.
    """

    def render(self, component, context, engine, area):
        """
        Add the picture at its declared pixel size.
        """
        add_picture(area, self.get_data(component), width=emu(component.width), height=emu(component.height))

    @classmethod
    def get_data(cls, component):
        """
        Decode the image into bytes Word can embed (PNG, JPEG, GIF or BMP).
        """
        uri = AssetResolver.resolve(component.src)
        mime, payload = cls.parse_uri(uri, component.src)
        return cls.decode(payload, component.src)

    @staticmethod
    def parse_uri(uri, source):
        """
        Validate the image data URI and return its MIME type and base64 payload.
        """
        if not uri.startswith("data:"):
            raise WordExportError(f"Word export embeds local images only; remote image refused: {source}")

        mime, separator, payload = uri[5:].partition(";base64,")
        if not separator or mime not in WORD_IMAGE_TYPES:
            raise WordExportError(f"Word cannot embed {mime} images ({source}); use PNG or JPEG.")

        return mime, payload

    @staticmethod
    def decode(payload, source):
        """
        Decode the base64 image payload into a binary stream for Word.
        """
        try:
            return BytesIO(base64.b64decode(payload, validate=True))
        except binascii.Error as error:
            raise WordExportError(f"Image data is not valid base64: {source}") from error


class QRCodeRenderer:
    """
    Render a QR code as a PNG picture centred in its area.
    """

    def render(self, component, context, engine, area):
        """
        Add the QR code at its declared pixel size.
        """
        size = Emu(component.size * EMU_PER_PIXEL)
        add_picture(area, QRCodeImage(component).png(), width=size, height=size)