from dataclasses import dataclass

from ...core.component import Component
from ...validators.media.qr_code import QRCodeValidator


@dataclass(kw_only=True)
class QRCode(Component):
    """
    Represent a QR code that encodes a prepared value, such as a link or an invoice reference.
    """

    value: str
    size: int = 96
    error_correction: str = "M"
    quiet_zone: int = 2
    alt: str = ""

    def __post_init__(self):
        """
        Validate the QR code properties.
        """
        QRCodeValidator.validate(self)
