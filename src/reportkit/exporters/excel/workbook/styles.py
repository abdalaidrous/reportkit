import re
import shutil
from zipfile import ZIP_DEFLATED, ZipFile


APPLY_FLAGS = re.compile(r'<xf\b[^>]*\bxfId="\d+"[^>]*/?>')
APPLY_NAMES = ("applyNumberFormat", "applyFont", "applyFill", "applyBorder", "applyAlignment")
STYLES_PART = "xl/styles.xml"


def copy_with_apply_flags(source, target):
    """
    Copy the XLSX archive from source to target (a path or a binary stream), marking every cell format as applying
    its font, fill, border, alignment and number format: openpyxl omits these flags and some Excel builds then ignore
    fills and borders. Parts are copied in streamed blocks, so large sheets never sit in memory.
    """
    with ZipFile(source) as archive, ZipFile(target, "w", ZIP_DEFLATED) as copy:
        for item in archive.infolist():
            if item.filename == STYLES_PART:
                copy_styles(archive, copy, item)
            else:
                copy_part(archive, copy, item)


def copy_styles(archive, copy, item):
    """
    Copy the workbook styles after adding missing apply flags to its cell formats.
    """
    styles = archive.read(item).decode("utf-8")
    styles = APPLY_FLAGS.sub(add_apply_flags, styles)
    copy.writestr(item, styles.encode("utf-8"))


def copy_part(archive, copy, item):
    """
    Copy an archive part in streamed blocks without loading its complete contents into memory.
    """
    with archive.open(item) as source, copy.open(item, "w") as target:
        shutil.copyfileobj(source, target)


def add_apply_flags(match):
    """
    Add the apply flags that one cell format element is missing.
    """
    element = match.group(0)
    missing = " ".join(f'{flag}="1"' for flag in APPLY_NAMES if not re.search(rf'\b{flag}\s*=', element))
    return element.replace("<xf ", f"<xf {missing} ", 1) if missing else element
