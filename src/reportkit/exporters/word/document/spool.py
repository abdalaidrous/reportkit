import re
from tempfile import SpooledTemporaryFile

from lxml import etree

MARKER = "rk-rows-{}"
MEMORY_LIMIT = 8 * 1024 * 1024
NAMESPACE_DECLARATION = re.compile(r'\s+xmlns(?::\w+)?="[^"]*"')


class RowSpool:
    """
    Keep the serialized XML of finished table rows outside the document tree, in temporary storage (memory up to a
    limit, then disk), so a large table no longer holds every row in memory; the rows are spliced back on save.
    """

    def __init__(self):
        """
        Start without segments.
        """
        self.segments = {}

    def segment(self):
        """
        Open a segment for one table and return its marker comment, placed in the tree where its rows belong.
        """
        name = MARKER.format(len(self.segments))
        self.segments[name] = SpooledTemporaryFile(max_size=MEMORY_LIMIT)
        return etree.Comment(name)

    def write(self, marker, rows):
        """
        Serialize rows into the marker's segment and remove them from the tree.
        """
        storage = self.segments[marker.text]
        for row in rows:
            storage.write(self.serialize(row))
            row.getparent().remove(row)

    @staticmethod
    def serialize(row):
        """
        Serialize one row without the namespace declarations lxml repeats on it; the document root declares them.
        """
        xml = etree.tostring(row, encoding="unicode")
        end = xml.index(">")
        return (NAMESPACE_DECLARATION.sub("", xml[:end]) + xml[end:]).encode("utf-8")

    def copy(self, name, target, block=1024 * 1024):
        """
        Copy one segment into a binary target.
        """
        storage = self.segments[name]
        storage.seek(0)
        while data := storage.read(block):
            target.write(data)

    def close(self):
        """
        Release the temporary storage.
        """
        for storage in self.segments.values():
            storage.close()
        self.segments = {}
