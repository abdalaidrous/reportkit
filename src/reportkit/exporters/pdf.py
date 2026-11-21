import logging
from contextlib import contextmanager
from functools import cache
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

from .base import BaseExporter
from .html.exporter import HtmlExporter
from .registry import ExporterRegistry

WEASYPRINT_HELP = 'PDF export requires WeasyPrint and its system libraries (Pango). Install it with: pip install "reportkit[pdf]" and see https://doc.courtbouillon.org/weasyprint/stable/first_steps.html'


class PdfExportError(RuntimeError):
    """
    Raised when the report cannot be converted to a complete PDF; the original error is kept as the cause.
    """


class PdfExporter(BaseExporter):
    """
    Export a report to PDF bytes by converting the complete HtmlExporter output with WeasyPrint.
    """

    @classmethod
    def export(cls, document, context=None, base_url=None) -> bytes:
        """
        Render the report through HtmlExporter and convert it; base_url is the only folder local files may come from.
        """
        return cls.convert(HtmlExporter().export(document, context).decode("utf-8"), base_url)

    @classmethod
    def convert(cls, html, base_url=None) -> bytes:
        """
        Convert complete report HTML into PDF bytes.
        """
        with conversion(cls.load_weasyprint()):
            return cls.render(html, base_url).write_pdf()

    @classmethod
    def render(cls, html, base_url=None):
        """
        Lay the HTML out into pages and return the WeasyPrint document.
        """
        weasyprint = cls.load_weasyprint()
        root = resolve_root(base_url)
        with conversion(weasyprint):
            return weasyprint.HTML(string=html, base_url=root.as_uri() + "/" if root else None, url_fetcher=fetcher_class(weasyprint)(root)).render()

    @staticmethod
    def load_weasyprint():
        """
        Import WeasyPrint lazily so it stays an optional dependency.
        """
        try:
            import weasyprint
        except (ImportError, OSError) as error:
            raise ImportError(WEASYPRINT_HELP) from error
        return weasyprint


class ErrorCollector(logging.Handler):
    """
    Collect the errors WeasyPrint logs when it skips a resource instead of failing.
    """

    def __init__(self):
        """
        Listen to error records only.
        """
        super().__init__(logging.ERROR)
        self.messages = []

    def emit(self, record):
        """
        Keep the formatted message.
        """
        self.messages.append(record.getMessage())


@contextmanager
def conversion(weasyprint):
    """
    Turn WeasyPrint failures and skipped resources into PdfExportError, keeping the original error as the cause.
    """
    logger, collector = logging.getLogger("weasyprint"), ErrorCollector()
    logger.addHandler(collector)
    try:
        yield
    except PdfExportError:
        raise
    except (Exception, weasyprint.urls.FatalURLFetchingError) as error:  # FatalURLFetchingError is a BaseException.
        raise PdfExportError(f"PDF export failed: {error.__cause__ or error}") from error
    finally:
        logger.removeHandler(collector)
    if collector.messages:
        raise PdfExportError("PDF export skipped resources: " + "; ".join(collector.messages))


@cache
def fetcher_class(weasyprint):
    """
    Build, once per WeasyPrint module, the URLFetcher subclass that enforces the resource policy.
    """

    class ReportResourceFetcher(weasyprint.urls.URLFetcher):
        """
        Fetch data URIs and files under root only; any other request fails the export.
        """

        def __init__(self, root):
            """
            Allow only data and file protocols and make every fetch error fatal.
            """
            super().__init__(allowed_protocols={"data", "file"}, fail_on_errors=True)
            self.root = root

        def fetch(self, url, headers=None):
            """
            Fetch an allowed resource or raise with the refused URL.
            """
            if not is_allowed_resource(url, self.root):
                raise PermissionError(f"Resource refused during PDF export (not embedded and not a file inside base_url): {url}")
            return super().fetch(url, headers)

    return ReportResourceFetcher


def resolve_root(base_url):
    """
    Resolve base_url (a folder path or file:// URI) to a real existing folder, or None.
    """
    if base_url is None:
        return None
    path = file_path(base_url) if str(base_url).startswith("file:") else Path(base_url)
    root = path.resolve() if path else None
    if root is None or not root.is_dir():
        raise ValueError(f"base_url must be an existing folder: {base_url}")
    return root


def file_path(url):
    """
    Convert a local file:// URI to a path; remote hosts (UNC shares) return None.
    """
    parsed = urlparse(str(url))
    if parsed.scheme != "file" or parsed.netloc not in ("", "localhost"):
        return None
    return Path(url2pathname(parsed.path))


def is_allowed_resource(url, root):
    """
    Allow data URIs, and existing files whose real path (symlinks resolved) is inside root.
    """
    if urlparse(url).scheme == "data":
        return True
    path = file_path(url) if root is not None else None
    if path is None:
        return False
    try:
        real = path.resolve(strict=True)
    except (OSError, RuntimeError):
        return False
    return real.is_file() and real.is_relative_to(root)


ExporterRegistry.register("pdf", PdfExporter)
