from collections import deque
from dataclasses import dataclass, field
from itertools import islice

from ....components.document import Footer, Header, Page

END = object()

class RowStream:
    """
    Read the rows of one page-level table lazily; rows stay pending until a chunk that laid them out is kept.
    """

    def __init__(self, table):
        """
        Start reading the table rows without materializing them.
        """
        self.table = table
        self.rows = iter(table.rows)
        self.pending = deque()
        self.started = False
        self.widths = None

    def peek(self, count):
        """
        Return up to count rows from the current position without consuming them.
        """
        while len(self.pending) < count:
            row = next(self.rows, END)
            if row is END:
                break
            self.pending.append(row)
        return list(islice(self.pending, count))

    def has_more_than(self, count):
        """
        Return whether rows remain after the first count pending rows.
        """
        return len(self.peek(count + 1)) > count

    def consume(self, count):
        """
        Drop the rows a kept chunk laid out.
        """
        for _ in range(count):
            self.pending.popleft()


@dataclass(frozen=True)
class Segment:
    """
    Consecutive report-level children: the children of one Page, or children placed directly in the Report.
    """

    page: Page | None
    children: list


@dataclass
class ReportFlow:
    """
    The position reached in a report: chunks before it are laid out, and the table at it may be partly consumed.
    """

    document: object
    segments: list = field(init=False)
    position: tuple = (0, 0)
    running: list = field(default_factory=list)
    streams: dict = field(default_factory=dict)

    def __post_init__(self):
        """
        Split the report children into segments.
        """
        self.segments = []
        loose = []
        for child in self.document.children:
            if isinstance(child, Page):
                if loose:
                    self.segments.append(Segment(None, loose))
                    loose = []
                self.segments.append(Segment(child, child.children))
            else:
                loose.append(child)
        if loose:
            self.segments.append(Segment(None, loose))

    def stream(self, position, table):
        """
        Return the row stream of the table at position, kept across planning attempts so lazy rows are read once.
        """
        if position not in self.streams:
            self.streams[position] = RowStream(table)
        return self.streams[position]

    def advance(self, position, running):
        """
        Move to the open table of a kept chunk, forgetting the tables before it.
        """
        self.position = position
        self.running.extend(running)
        self.streams = {position: self.streams[position]}

    @staticmethod
    def is_running(component):
        """
        Return whether the component repeats in the page margins.
        """
        return isinstance(component, (Header, Footer)) and component.repeat
