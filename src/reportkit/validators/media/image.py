FITS = {"contain", "cover", "fill", "none", "scale-down"}


class ImageValidator:
    """
    Validate Image definitions.
    """

    @staticmethod
    def validate(image):
        """
        The source is a non-empty string and the fit a CSS object-fit value.
        """
        if not isinstance(image.src, str) or not image.src.strip():
            raise ValueError("Image source must be a non-empty string.")
        if image.fit not in FITS:
            raise ValueError("Unsupported image fit.")
