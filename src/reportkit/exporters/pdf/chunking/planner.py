from dataclasses import dataclass, field, replace

from ....components.table import Table
from .flow import ReportFlow
from .fragment import TableFragment


@dataclass
class Chunk:
    """
    One chunk of a report: a complete small report, and the table it stops inside unless it is the last chunk.
    """

    report: object
    position: tuple | None = None
    stream: object = None
    running: list = field(default_factory=list)
    rows: int = 0

    @property
    def final(self):
        """
        Return whether the chunk reaches the end of the report.
        """
        return self.position is None


class ChunkPlanner:
    """
    Build the next chunk from the flow position: everything up to about limit table rows, stopping inside a table.
    """

    @classmethod
    def plan(cls, flow, limit):
        """
        Collect children from the flow position; planning never moves the flow, so a chunk can be planned again.
        """
        parts, running, position, stream, rows = cls.collect(flow, limit)
        return Chunk(cls.build(flow, parts), position, stream, running, rows)

    @classmethod
    def collect(cls, flow, limit):
        """
        Collect segments until a table requires continuation.
        """
        parts, running, rows = [], [], 0
        first_segment, first_child = flow.position

        for segment_index in range(first_segment, len(flow.segments)):
            segment = flow.segments[segment_index]
            children = []
            parts.append((segment, children))

            start = first_child if segment_index == first_segment else 0
            rows, position, stream, taken = cls.collect_segment(flow, segment_index, start, children, running, rows, limit)

            if position is not None:
                return parts, running, position, stream, taken

        return parts, running, None, None, 0

    @classmethod
    def collect_segment(cls, flow, segment_index, start, children, running, rows, limit):
        """
        Collect children from one segment, stopping when a table has more rows; returns the rows so far, and the
        open table's position, stream and fragment row count.
        """
        segment = flow.segments[segment_index]

        for child_index in range(start, len(segment.children)):
            child = segment.children[child_index]

            if not isinstance(child, Table):
                cls.append_child(child, children, running)
                continue

            position = (segment_index, child_index)
            stream, taken, more = cls.read_table(flow, position, child, limit, rows)
            cls.append_table(child, stream, taken, more, children)
            rows += len(taken)

            if more:
                return rows, position, stream, len(taken)

        return rows, None, None, 0

    @staticmethod
    def append_child(child, children, running):
        """
        Append a non-table child and track repeating elements for the next chunk.
        """
        children.append(child)

        if ReportFlow.is_running(child):
            running.append(child)

    @classmethod
    def read_table(cls, flow, position, table, limit, rows):
        """
        Peek at the next table rows without advancing the flow or consuming the stream.
        """
        stream = flow.stream(position, table)
        taken = stream.peek(cls.take(limit, rows))
        more = stream.has_more_than(len(taken))
        return stream, taken, more

    @staticmethod
    def append_table(table, stream, taken, more, children):
        """
        Build a table fragment from the selected rows, preserving continuation state and column widths.
        """
        fragment = TableFragment.of(table, taken, continued=stream.started, last=not more, widths=stream.widths)
        children.append(fragment)

    @staticmethod
    def take(limit, rows):
        """
        Fill the chunk up to limit rows; a table reached when the chunk is already half full gets a full limit, so
        the chunk does not stop a few rows into it.
        """
        remaining = limit - rows
        return remaining if remaining * 2 >= limit else limit

    @classmethod
    def build(cls, flow, parts):
        """
        Rebuild the report around the collected children, starting with the repeating headers and footers already passed.
        """
        children = []

        for index, (segment, items) in enumerate(parts):
            if index == 0:
                items = [*flow.running, *items]

            children.extend(cls.build_segment(segment, items))

        return replace(flow.document, children=children)

    @staticmethod
    def build_segment(segment, items):
        """
        Rebuild a page with its collected children, or return the children directly for segments without a page.
        """
        if segment.page is None:
            return items

        return [replace(segment.page, children=items)]