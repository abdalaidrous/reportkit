from ..components.table import TableCell


def get_entries(component, table_row):
    """
    Pair each value or explicit cell with its column definition (None for explicit cells).
    """
    if table_row.cells is not None:
        return [(cell, None) for cell in table_row.cells]
    return [(table_row.values.get(column.key), column) for column in component.columns]


def place_cells(entries, start, row, occupied):
    """
    Yield (column, entry, colspan, rowspan) in order, skipping positions held by earlier row spans.
    """
    column = start
    for entry in entries:
        column = skip_occupied(column, row, occupied)
        colspan, rowspan = get_spans(entry)
        check_free(column, colspan, row, occupied)
        occupied.update((row + offset, column + shift) for offset in range(1, rowspan) for shift in range(colspan))
        yield column, entry, colspan, rowspan
        column += colspan
    occupied.difference_update({position for position in occupied if position[0] == row})


def skip_occupied(column, row, occupied):
    """
    Move past the positions a row span from an earlier row still holds.
    """
    while (row, column) in occupied:
        column += 1
    return column


def check_free(column, colspan, row, occupied):
    """
    Refuse a column span that would overlap a row span from an earlier row.
    """
    if any((row, column + shift) in occupied for shift in range(colspan)):
        raise ValueError(f"A cell spanning {colspan} columns overlaps a row span from an earlier row (row {row}).")


def get_spans(entry):
    """
    Return the colspan and rowspan of an entry; plain values span one cell.
    """
    return (entry[0].colspan, entry[0].rowspan) if isinstance(entry[0], TableCell) else (1, 1)


def header_text(column, separator):
    """
    Join a column title and subtitle.
    """
    return f"{column.title}{separator}{column.subtitle}" if column.subtitle else column.title
