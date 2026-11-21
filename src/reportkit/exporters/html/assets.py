import base64
import mimetypes
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname


class AssetResolver:
    """Resolve image assets for portable HTML and PDF output."""

    @classmethod
    def resolve(cls, source):
        """Resolve an image source into a portable URI."""
        if not source:
            return source

        source = str(source)

        if cls.is_remote(source):
            return source

        path = cls.resolve_path(source)
        cls.validate_path(path)
        mime = cls.resolve_mime(path)
        return cls.encode_image(path, mime)

    @staticmethod
    def is_remote(source):
        """Check whether the source is already a supported URI."""
        return source.startswith(("http://", "https://", "data:image/"))

    @classmethod
    def resolve_path(cls, source):
        """Resolve a local path or file URI."""
        parsed = urlparse(source)

        if parsed.scheme == "file":
            return cls.resolve_file_uri(parsed)

        return Path(source)

    @staticmethod
    def resolve_file_uri(parsed):
        """Convert a file URI into a local filesystem path."""
        raw_path = url2pathname(unquote(parsed.path))

        if parsed.netloc:
            raw_path = f"//{parsed.netloc}{raw_path}"

        return Path(raw_path)

    @staticmethod
    def validate_path(path):
        """Ensure the image file exists."""
        if not path.is_file():
            raise FileNotFoundError(f"Image asset not found: {path}")

    @staticmethod
    def resolve_mime(path):
        """Resolve and validate the image MIME type."""
        mime, _ = mimetypes.guess_type(path.name)

        if not mime or not mime.startswith("image/"):
            raise ValueError(f"Unsupported image asset: {path}")

        return mime

    @staticmethod
    def encode_image(path, mime):
        """Encode a local image as a data URI."""
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{encoded}"