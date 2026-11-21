import base64
import binascii
from io import BytesIO

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Emu

from ...html.assets import AssetResolver
from ..exceptions import WordExportError

WORD_IMAGE_TYPES = ("image/png", "image/jpeg", "image/gif", "image/bmp")
EMU_PER_PIXEL = 9525


class ImageRenderer:
    """
    Render an Image centred in its area; local files are embedded through AssetResolver.
    """

    def render(self, component, context, engine, area):
        """
        Add the picture at its declared pixel size.
        """
        paragraph = area.paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.add_run().add_picture(self.get_data(component), width=emu(component.width), height=emu(component.height))

    @staticmethod
    def get_data(component):
        """
        Decode the image into bytes Word can embed (PNG, JPEG, GIF or BMP).
        """
        uri = AssetResolver.resolve(component.src)
        if not uri.startswith("data:"):
            raise WordExportError(f"Word export embeds local images only; remote image refused: {component.src}")
        mime, _, payload = uri[len("data:"):].partition(";base64,")
        if mime not in WORD_IMAGE_TYPES:
            raise WordExportError(f"Word cannot embed {mime} images ({component.src}); use PNG or JPEG.")
        try:
            return BytesIO(base64.b64decode(payload, validate=True))
        except binascii.Error as error:
            raise WordExportError(f"Image data is not valid base64: {component.src}") from error


def emu(value):
    """
    Convert a pixel size such as "76" or "76px" into a Word length, or None.
    """
    return Emu(int(value.removesuffix("px")) * EMU_PER_PIXEL) if value and value.removesuffix("px").isdigit() else None
