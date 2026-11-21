from dataclasses import dataclass

from ....rendering.tracks import distribute


@dataclass(frozen=True)
class Region:
    """
    Describe where a formatted renderer writes: the top row, the first grid column and the number of grid columns.
    """

    row: int
    column: int
    width: int

    def below(self, rows):
        """
        Return the same region moved down by a number of rows.
        """
        return Region(self.row + rows, self.column, self.width)

    def split(self, shares):
        """
        Split the region into side-by-side slots sized by their shares of the width.
        """
        widths = distribute(shares, self.width)
        return [Region(self.row, self.column + sum(widths[:index]), width) for index, width in enumerate(widths)]
