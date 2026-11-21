from ..dependencies import load_weasyprint
from .fragment import FRAGMENT_CLASS


class ChunkLayout:
    """
    Read a laid out chunk that stops inside a table: its last page is dropped and laid out again with the next chunk,
    so every kept page breaks exactly where a single-pass layout would.
    """

    def __init__(self, pages):
        """
        Find the open fragment, the last table fragment on the last page.
        """
        self.pages = pages
        self.kept = pages[:-1]
        self.container, self.table = self.find_open_fragment()

    def find_open_fragment(self):
        """
        Return the last table fragment on the final page, or None when no fragment exists.
        """
        found = self.fragments(self.pages[-1]) if self.pages else []
        return found[-1] if found else (None, None)

    @property
    def accepted(self):
        """
        The last page can be dropped only when it holds nothing but rows of the open fragment, which is true when the
        fragment already started on the page before.
        """
        return self.container is not None and len(self.pages) >= 2 and self.continues_from_previous()

    def continues_from_previous(self):
        """
        Return whether the open fragment also appears on the page before the last page.
        """
        return any(container is self.container for container, _ in self.fragments(self.pages[-2]))

    def consumed_rows(self):
        """
        Count the fragment rows laid out on the kept pages; a row split onto the dropped page is laid out again.
        """
        kept = self.collect_rows(self.kept)
        dropped = set(self.body_rows(self.pages[-1]))
        return len(kept - dropped)

    def collect_rows(self, pages):
        """
        Collect the open fragment's body rows across the given pages without counting repeated rows.
        """
        return {row for page in pages for row in self.body_rows(page)}

    def column_widths(self):
        """
        Return the used column widths of the open fragment, in column order.
        """
        return [column.width for group in self.table.column_groups for column in group.children]

    def body_rows(self, page):
        """
        Return the elements of the open fragment's body rows laid out on the page.
        """
        for container, table in self.fragments(page):
            if container is self.container:
                return self.table_rows(table)

        return []

    @staticmethod
    def table_rows(table):
        """
        Return the body row elements of a table, excluding repeated header and footer rows.
        """
        return [row.element for group in table.children if not (group.is_header or group.is_footer) for row in group.children]

    @classmethod
    def fragments(cls, page):
        """
        Return (container element, outer table box) for every table fragment laid out on the page.
        """
        table_box = load_weasyprint().formatting_structure.boxes.TableBox
        found = []

        for box in page._page_box.descendants():
            if not cls.is_fragment(box):
                continue

            table = cls.find_table(box, table_box)

            if table is not None:
                found.append((box.element, table))

        return found

    @staticmethod
    def is_fragment(box):
        """
        Return whether the box represents a report table fragment container.
        """
        return box.element_tag == "div" and FRAGMENT_CLASS in (box.element.get("class") or "").split()

    @staticmethod
    def find_table(box, table_box):
        """
        Find the first table box inside a fragment container.
        """
        return next((child for child in box.descendants() if isinstance(child, table_box)), None)