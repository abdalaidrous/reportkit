from functools import cache


def get_fetcher(weasyprint, policy):
    """
    Return a WeasyPrint 70 URL fetcher that enforces the given resource policy.
    """
    return get_fetcher_class(weasyprint)(policy)


@cache
def get_fetcher_class(weasyprint):
    """
    Build the URLFetcher subclass once per WeasyPrint module; WeasyPrint is optional, so it cannot be subclassed at import time.
    """

    class PdfResourceFetcher(weasyprint.urls.URLFetcher):
        """
        Fetch only resources the policy allows; every refused or failed fetch stops the conversion.
        """

        def __init__(self, policy):
            """
            Allow only data and file protocols and make every fetch error fatal.
            """
            super().__init__(allowed_protocols={"data", "file"}, fail_on_errors=True)
            self.policy = policy

        def fetch(self, url, headers=None):
            """
            Fetch an allowed resource or raise with the refused URL.
            """
            if not self.policy.is_allowed(url):
                raise PermissionError(f"Resource refused during PDF export (not embedded and not a file inside base_url): {url}")
            return super().fetch(url, headers)

    return PdfResourceFetcher
