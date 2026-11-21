import re
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

APPLY_FLAGS = re.compile(r"<xf [^>]*?xfId=\"\d+\"[^>]*?/?>")
APPLY_NAMES = ("applyNumberFormat", "applyFont", "applyFill", "applyBorder", "applyAlignment")


def with_apply_flags(xlsx):
    """
    Mark every cell format as applying its font, fill, border, alignment and number format: openpyxl omits these
    flags and some Excel builds then ignore fills and borders.
    """
    source, target = ZipFile(BytesIO(xlsx)), BytesIO()
    with ZipFile(target, "w", ZIP_DEFLATED) as archive:
        for item in source.infolist():
            data = source.read(item.filename)
            archive.writestr(item, APPLY_FLAGS.sub(add_apply_flags, data.decode("utf-8")) if item.filename == "xl/styles.xml" else data)
    return target.getvalue()


def add_apply_flags(match):
    """
    Add the apply flags that one cell format element is missing.
    """
    missing = " ".join(f'{flag}="1"' for flag in APPLY_NAMES if flag not in match.group(0))
    return match.group(0).replace("<xf ", f"<xf {missing} ", 1) if missing else match.group(0)
