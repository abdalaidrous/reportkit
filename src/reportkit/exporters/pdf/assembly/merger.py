from io import BytesIO

from ..dependencies import load_pypdf


class PdfMerger:
    """
    Merge chunk PDFs in order with pypdf, stamp the page numbers on top, and write the result to the target.
    """

    def __init__(self):
        """
        Start an empty merged document.
        """
        self.pypdf = load_pypdf()
        self.writer = self.pypdf.PdfWriter()

    def append(self, pdf):
        """
        Append every page of one chunk; the first chunk also gives the document metadata (title, producer).
        """
        reader = self.pypdf.PdfReader(BytesIO(pdf))
        if not self.writer.pages and reader.metadata:
            self.writer.add_metadata(dict(reader.metadata))
        for page in reader.pages:
            self.writer.add_page(page)

    @property
    def page_count(self):
        """
        Return the number of merged pages.
        """
        return len(self.writer.pages)

    def stamp(self, overlays):
        """
        Draw each overlay page on the merged page with the same number, in order.
        """
        pages = iter(self.writer.pages)
        for pdf in overlays:
            for overlay, page in zip(self.pypdf.PdfReader(BytesIO(pdf)).pages, pages):
                page.merge_page(overlay)
                page.compress_content_streams()

    def write(self, target):
        """
        Write the merged PDF to a path or a binary stream.
        """
        self.writer.write(target)
