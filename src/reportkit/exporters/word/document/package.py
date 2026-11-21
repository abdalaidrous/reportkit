import re
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

MAIN_PART = "word/document.xml"
MARKER_COMMENT = re.compile(rb"<!--(rk-rows-\d+)-->")


class DocxPackage:
    """
    Rewrite a saved DOCX package into the target, streaming the spooled table rows into the main document part where
    their markers are, so the full document XML is never built in memory.
    """

    @classmethod
    def write(cls, source, spool, target):
        """
        Copy every part of the source package to the target, with the spooled rows spliced into the main part.
        """
        with ZipFile(BytesIO(source)) as package, ZipFile(target, "w", ZIP_DEFLATED) as output:
            for info in package.infolist():
                if info.filename == MAIN_PART:
                    cls.write_main_part(package.read(info), info, spool, output)
                else:
                    output.writestr(info, package.read(info), ZIP_DEFLATED)

    @staticmethod
    def write_main_part(xml, info, spool, output):
        """
        Write the main part piece by piece: the XML between markers, then each marker's spooled rows.
        """
        info.compress_type = ZIP_DEFLATED
        with output.open(info, "w", force_zip64=True) as part:
            position = 0
            for match in MARKER_COMMENT.finditer(xml):
                part.write(xml[position:match.start()])
                spool.copy(match.group(1).decode("ascii"), part)
                position = match.end()
            part.write(xml[position:])
