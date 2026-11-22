ERROR_CORRECTIONS = {"L", "M", "Q", "H"}
MAX_QUIET_ZONE = 10


class QRCodeValidator:
    """
    Validate QRCode definitions.
    """

    @classmethod
    def validate(cls, code):
        """
        Run every QR code rule.
        """
        cls.validate_value(code.value)
        cls.validate_presentation(code)

    @staticmethod
    def validate_value(value):
        """
        The encoded value is a non-empty string.
        """
        if not isinstance(value, str) or not value:
            raise ValueError("QR code value must be a non-empty string.")

    @staticmethod
    def validate_presentation(code):
        """
        Validate the size in pixels, the error correction level and the quiet zone in modules.
        """
        if not is_integer(code.size) or code.size <= 0:
            raise ValueError("QR code size must be a positive number of pixels.")
        if code.error_correction not in ERROR_CORRECTIONS:
            raise ValueError("QR code error correction must be one of L, M, Q or H.")
        if not is_integer(code.quiet_zone) or not 0 <= code.quiet_zone <= MAX_QUIET_ZONE:
            raise ValueError(f"QR code quiet zone must be an integer between 0 and {MAX_QUIET_ZONE}.")
        if not isinstance(code.alt, str):
            raise TypeError("QR code alt text must be a string.")


def is_integer(value):
    """
    Return whether the value is an integer (bool excluded).
    """
    return isinstance(value, int) and not isinstance(value, bool)
