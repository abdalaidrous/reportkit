from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    """
    Describe where a formatted renderer writes: the top row, the first column and the number of columns available.
    """

    row: int
    column: int
    width: int

    def below(self, rows):
        """
        Return the same region moved down by a number of rows.
        """
        return Region(self.row + rows, self.column, self.width)

    def split(self, count):
        """
        Split the region into side-by-side slots; the last slot takes the remaining columns.
        """
        size = max(1, self.width // count)
        widths = [size] * (count - 1) + [max(1, self.width - size * (count - 1))]
        return [Region(self.row, self.column + sum(widths[:index]), width) for index, width in enumerate(widths)]
