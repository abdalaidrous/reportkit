from docx.oxml.ns import qn
from docx.table import _Row


FLUSH_ROWS = 200


class TableRows:
    """
    Manage Word table rows with absolute indexing and incremental spooling.
    """

    def __init__(self, table, spool):
        """
        Initialize the table rows and spooling state.
        """
        self.table = table
        self.tbl = table._tbl
        self.spool = spool if self.is_document_table() else None
        self.widths = self.get_column_widths()
        self.count = 0
        self.held = 0
        self.flushed = 0
        self.marker = None

    def add(self):
        """
        Create a row with the configured column widths.
        """
        tr = self.tbl.add_tr()
        self.add_cells(tr)

        number = self.count
        self.count += 1

        return _Row(tr, self.table), number

    def add_cells(self, tr):
        """
        Create and size the cells of a new row.
        """
        for width in self.widths:
            tc = tr.add_tc()

            if width is not None:
                tc.width = width

    def hold(self):
        """
        Keep the existing header rows in the table.
        """
        self.held = self.count

    def cell(self, number, column):
        """
        Return a cell using its absolute row number.
        """
        row = _Row(self.tbl.tr_lst[self.index(number)], self.table)
        return row.cells[column]

    def index(self, number):
        """
        Resolve an absolute row number to its current table index.
        """
        return number if number < self.held else number - self.flushed

    def flush(self, keep_from):
        """
        Spool completed body rows when the flush threshold is reached.
        """
        if not self.can_flush(keep_from):
            return

        rows = self.get_flushable_rows(keep_from)
        self.ensure_marker(rows)
        self.spool.write(self.marker, rows)
        self.flushed += len(rows)

    def can_flush(self, keep_from):
        """
        Check whether enough completed rows are available for spooling.
        """
        return self.spool is not None and keep_from - self.held - self.flushed >= FLUSH_ROWS

    def get_flushable_rows(self, keep_from):
        """
        Return completed body rows eligible for spooling.
        """
        return self.tbl.tr_lst[self.held:self.index(keep_from)]

    def ensure_marker(self, rows):
        """
        Create the spool marker before the first flushed row.
        """
        if self.marker is not None:
            return

        self.marker = self.spool.segment()
        rows[0].addprevious(self.marker)

    def get_column_widths(self):
        """
        Return the table grid column widths.
        """
        return [column.w for column in self.tbl.tblGrid.gridCol_lst]

    def is_document_table(self):
        """
        Check whether the table belongs directly to the document body.
        """
        return self.tbl.getparent().tag == qn("w:body")