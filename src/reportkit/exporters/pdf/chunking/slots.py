import json
from dataclasses import dataclass, replace

from ...html.page.components import HtmlPageComponentFinder
from ..dependencies import load_weasyprint


DEFERRED_CLASS = "rk-page-count--deferred"
FORMAT_ATTRIBUTE = "data-rk-page-count"
PHYSICAL_ALIGNMENTS = {("start", "ltr"): "left", ("start", "rtl"): "right", ("end", "ltr"): "right", ("end", "rtl"): "left"}


@dataclass(frozen=True)
class PageCountSlot:
    """
    Where a deferred PageCount was laid out in a chunk: its merged page index, its first line relative to the page
    content area (CSS px), its format and the computed text style needed to stamp the page total in its place.
    """

    page: int
    left: float
    top: float
    width: float
    height: float
    format: str
    font_family: str
    font_size: float
    font_weight: int
    color: str
    align: str
    direction: str

    def moved(self, pages):
        """
        Return the slot moved forward by a number of pages, once the chunk's place in the merged PDF is known.
        """
        return replace(self, page=self.page + pages)

    def text(self, total):
        """
        Return the line to stamp for the merged page total.
        """
        return self.format.replace("{pages}", str(total))


class PageCountLedger:
    """
    Collect the page count slots of the chunks in merged page order.
    """

    def __init__(self, document):
        """
        Start empty; slots are looked for only when the report has a PageCount.
        """
        self.enabled = bool(HtmlPageComponentFinder.find(document).counts)
        self.slots = []
        self.pages = 0

    def laid_out(self, pages):
        """
        Return the number of pages and the slots laid out on them.
        """
        return PageCountSlots.laid_out(pages, self.enabled)

    def keep(self, laid_out):
        """
        Place a kept chunk's slots after the pages already kept.
        """
        pages, slots = laid_out
        self.slots.extend(slot.moved(self.pages) for slot in slots)
        self.pages += pages


class PageCountSlots:
    """
    Find the deferred PageCount lines of a laid out chunk, including those inside repeating headers and footers.
    """

    @classmethod
    def laid_out(cls, pages, enabled):
        """
        Return the number of pages and their slots; enabled is False when the report has no PageCount.
        """
        return len(pages), cls.find(pages) if enabled else []

    @classmethod
    def find(cls, pages):
        """
        Return the slots of the pages, numbered from 0 in the order given.
        """
        block_box = load_weasyprint().formatting_structure.boxes.BlockBox
        return [slot for index, page in enumerate(pages) for slot in cls.page_slots(page._page_box, index, block_box)]

    @classmethod
    def page_slots(cls, page_box, index, block_box):
        """
        Yield one slot per deferred PageCount block laid out on the page.
        """
        origin = cls.page_origin(page_box)

        for box in page_box.descendants():
            if isinstance(box, block_box) and cls.is_deferred(box):
                yield cls.slot(box, index, origin)

    @staticmethod
    def page_origin(page_box):
        """
        Return the page content area's origin in CSS pixels.
        """
        return page_box.content_box_x(), page_box.content_box_y()

    @staticmethod
    def is_deferred(box):
        """
        Return whether the box is a PageCount laid out without its total.
        """
        return box.element_tag == "p" and DEFERRED_CLASS in (box.element.get("class") or "").split()

    @classmethod
    def slot(cls, box, index, origin):
        """
        Record the block's first line, geometry and computed text style.
        """
        line = box.children[0] if box.children else box
        style = box.style
        direction = style["direction"]

        return PageCountSlot(
            page=index,
            left=box.content_box_x() - origin[0],
            top=line.position_y - origin[1],
            width=box.width,
            height=line.height,
            format=box.element.get(FORMAT_ATTRIBUTE),
            font_family=cls.font_family(style),
            font_size=style["font_size"],
            font_weight=style["font_weight"],
            color=str(style["color"]),
            align=physical_alignment(style["text_align_all"], direction),
            direction=direction,
        )

    @staticmethod
    def font_family(style):
        """
        Format the computed font family names as a CSS font-family value.
        """
        return ", ".join(json.dumps(name, ensure_ascii=False) for name in style["font_family"])


def physical_alignment(align, direction):
    """
    Turn a computed text alignment into left, right or center; justified text aligns like start.
    """
    if align in ("left", "right", "center"):
        return align
    return PHYSICAL_ALIGNMENTS[("end" if align == "end" else "start", direction)]
