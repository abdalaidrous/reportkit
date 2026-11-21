import unittest

from reportkit.components.document import Footer, Header, Page
from reportkit.components.pagination import PageNumber
from reportkit.components.typography import Text

from .helpers import export_html


class PageResolverTests(unittest.TestCase):
    """Print CSS generation and validation."""

    def test_page_css_and_centered_number(self):
        html = export_html(Page(margin_top="10mm", page_number_position="bottom-center", children=[Text(value="x"), PageNumber(format="Page {page} of {pages}")]))
        self.assertIn("size: A4 portrait;", html)
        self.assertIn("margin: 10mm 15mm 15mm 15mm;", html)
        self.assertIn('@bottom-center { content: "Page " counter(page) " of " counter(pages); font-family:', html)

    def test_no_page_means_no_page_css(self):
        self.assertNotIn("@bottom", export_html(Text(value="x")))

    def test_invalid_page_settings(self):
        for page in (Page(size="B9"), Page(orientation="diagonal"), Page(margin_top="10px"), Page(page_number_position="middle")):
            with self.subTest(page=page), self.assertRaises(ValueError):
                export_html(page)

    def test_pages_must_match(self):
        with self.assertRaises(ValueError):
            export_html(Page(), Page(orientation="landscape"))

    def test_single_page_number(self):
        with self.assertRaises(ValueError):
            export_html(Page(children=[PageNumber(), PageNumber()]))

    def test_number_collides_with_running_footer(self):
        with self.assertRaises(ValueError):
            export_html(Page(page_number_position="bottom-center", children=[Footer(repeat=True), PageNumber()]))

    def test_running_header(self):
        html = export_html(Page(children=[Header(repeat=True, children=[Text(value="h")])]))
        self.assertIn("@top-center { content: element(rk-running-header); }", html)
        self.assertIn(".rk-running-header { position: running(rk-running-header); }", html)


if __name__ == "__main__":
    unittest.main()
