from docx.oxml.ns import qn
from docx.table import _Row

FLUSH_ROWS = 200


class TableRows:
    """
    Add rows to a Word table by absolute row number, in constant time per row (python-docx scans the whole table for
    add_row, len(rows) and cell), and move finished body rows of document-level tables to the document's row spool so
    only the rows a span can still reach stay in memory.
    """

    def __init__(self, table, spool):
        """
        Read the column widths once and start with no rows.
        """
        self.table = table
        self.tbl = table._tbl
        self.spool = spool if self.tbl.getparent().tag == qn("w:body") else None
        self.widths = [column.w for column in self.tbl.tblGrid.gridCol_lst]
        self.count = 0
        self.held = 0
        self.flushed = 0
        self.marker = None

    def add(self):
        """
        Append a row with one sized cell per column and return it with its absolute number.
        """
        tr = self.tbl.add_tr()
        for width in self.widths:
            tc = tr.add_tc()
            if width is not None:
                tc.width = width
        self.count += 1
        return _Row(tr, self.table), self.count - 1

    def hold(self):
        """
        Keep the rows added so far (the header) in the tree for good.
        """
        self.held = self.count

    def cell(self, number, column):
        """
        Return the cell of a row still in the tree by absolute row number.
        """
        return _Row(self.tbl.tr_lst[self.index(number)], self.table).cells[column]

    def index(self, number):
        """
        Convert an absolute row number into a position among the rows still in the tree.
        """
        return number if number < self.held else number - self.flushed

    def flush(self, keep_from):
        """
        Spool the body rows before absolute number keep_from once enough of them have collected.
        """
        if self.spool is None or keep_from - self.held - self.flushed < FLUSH_ROWS:
            return
        rows = self.tbl.tr_lst[self.held:self.index(keep_from)]
        if self.marker is None:
            self.marker = self.spool.segment()
            rows[0].addprevious(self.marker)
        self.spool.write(self.marker, rows)
        self.flushed += len(rows)
