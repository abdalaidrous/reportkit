from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname


class PdfResourcePolicy:
    """
    Decide which resources a PDF conversion may load: embedded data URIs always, local files only inside base_url.
    """

    def __init__(self, base_url=None):
        """
        Resolve the folder local files may come from.
        """
        self.root = self.resolve_root(base_url)

    @property
    def base_uri(self):
        """
        Return the root as a file URI for resolving relative URLs, or None.
        """
        return self.root.as_uri() + "/" if self.root else None

    def is_allowed(self, url):
        """
        Allow data URIs, and existing files whose real path (symlinks resolved) is inside the root.
        """
        if urlparse(url).scheme == "data":
            return True
        path = self.file_path(url) if self.root is not None else None
        if path is None:
            return False
        try:
            real = path.resolve(strict=True)
        except (OSError, RuntimeError):
            return False
        return real.is_file() and real.is_relative_to(self.root)

    @classmethod
    def resolve_root(cls, base_url):
        """
        Resolve base_url (a folder path or file:// URI) to a real existing folder, or None.
        """
        if base_url is None:
            return None
        path = cls.file_path(base_url) if str(base_url).startswith("file:") else Path(base_url)
        root = path.resolve() if path else None
        if root is None or not root.is_dir():
            raise ValueError(f"base_url must be an existing folder: {base_url}")
        return root

    @staticmethod
    def file_path(url):
        """
        Convert a local file:// URI to a path; remote hosts such as UNC shares return None.
        """
        parsed = urlparse(str(url))
        if parsed.scheme != "file" or parsed.netloc not in ("", "localhost"):
            return None
        return Path(url2pathname(parsed.path))
