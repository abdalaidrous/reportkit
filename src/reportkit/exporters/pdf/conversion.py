import logging
import threading
from contextlib import contextmanager

from ..html.templates import HtmlTemplateEngine
from .dependencies import load_weasyprint
from .exceptions import PdfExportError
from .resources import PdfResourcePolicy, get_fetcher

PDF_CSS = HtmlTemplateEngine().static_dir / "pdf.css"


class WeasyPrintErrorMonitor(logging.Handler):
    """
    Collect the errors WeasyPrint logs when it skips a resource, for the current thread only so concurrent conversions
    never see each other's errors.
    """

    def __init__(self):
        """
        Listen to error records logged by the thread that created the monitor.
        """
        super().__init__(logging.ERROR)
        self.thread = threading.get_ident()
        self.messages = []

    def __enter__(self):
        """
        Start listening to the WeasyPrint logger.
        """
        logging.getLogger("weasyprint").addHandler(self)
        return self

    def __exit__(self, *exc_info):
        """
        Stop listening without hiding any exception.
        """
        logging.getLogger("weasyprint").removeHandler(self)
        return False

    def filter(self, record):
        """
        Keep only records from the monitored thread.
        """
        return record.thread == self.thread

    def emit(self, record):
        """
        Keep the formatted message.
        """
        self.messages.append(record.getMessage())

    def raise_for_errors(self):
        """
        Fail when WeasyPrint skipped anything, so an incomplete PDF is never returned silently.
        """
        if self.messages:
            raise PdfExportError("PDF export skipped resources: " + "; ".join(self.messages))


class PdfConversionService:
    """
    Convert complete report HTML into PDF with WeasyPrint, adding the PDF-only stylesheet and the resource policy.
    """

    @classmethod
    def convert(cls, html, base_url=None) -> bytes:
        """
        Convert the HTML into PDF bytes.
        """
        policy = PdfResourcePolicy(base_url)
        with cls.guard() as weasyprint:
            return cls.layout(weasyprint, html, policy).write_pdf()

    @classmethod
    def render(cls, html, base_url=None):
        """
        Lay the HTML out into pages and return the WeasyPrint document.
        """
        policy = PdfResourcePolicy(base_url)
        with cls.guard() as weasyprint:
            return cls.layout(weasyprint, html, policy)

    @staticmethod
    def layout(weasyprint, html, policy):
        """
        Lay the HTML out with the resource fetcher and pdf.css.
        """
        return weasyprint.HTML(string=html, base_url=policy.base_uri, url_fetcher=get_fetcher(weasyprint, policy)).render(stylesheets=[weasyprint.CSS(string=PDF_CSS.read_text(encoding="utf-8"))])

    @staticmethod
    @contextmanager
    def guard():
        """
        Turn every failure of the whole conversion, including skipped resources, into PdfExportError with the original
        cause.
        """
        weasyprint = load_weasyprint()
        with WeasyPrintErrorMonitor() as monitor:
            try:
                yield weasyprint
            except (Exception, weasyprint.urls.FatalURLFetchingError) as error:  # FatalURLFetchingError is a BaseException.
                raise PdfExportError(f"PDF export failed: {error.__cause__ or error}") from error
        monitor.raise_for_errors()
