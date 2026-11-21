from ....components.table import TableCell
from ....styles.style import Style
from ....validators.table.table import TableValidator
from ..styles import table_styles
from ..values import component_text, number_format


class TableRenderer:
    """
    Render a Table in the formatted mode: caption, header, prepared rows and footer, with spans and table styles.
    """

    def render(self, component, context, engine, region):
        """
        Write the table rows in the order they arrive and return the rows used.
        """
        styles, occupied = table_styles(), set()
        row = region.row + self.render_caption(component, context, engine, region)
        row += self.render_header(component, engine, region.below(row - region.row), styles)
        for index, table_row in enumerate(component.rows):
            TableValidator.validate_row(table_row)
            self.render_row(component, table_row, index, engine, region.below(row - region.row), styles, occupied)
            row += 1
        if component.footer:
            self.render_row(component, component.footer, 0, engine, region.below(row - region.row), styles, occupied)
            row += 1
        self.set_widths(component, engine, region)
        return row - region.row

    def render_caption(self, component, context, engine, region):
        """
        Write the table caption across the region when the table has one.
        """
        if not component.header:
            return 0
        engine.sheet.write(region.row, region.column, component.header, Style(font_weight=700, font_size=18).merge(context.resolve_style(component)))
        engine.sheet.merge(region.row, region.column, max(region.width, len(component.columns)))
        return 1

    def render_header(self, component, engine, region, styles):
        """
        Write the column titles and subtitles, repeated on printed pages when requested.
        """
        if not component.table_style.show_header:
            return 0
        style = styles["header"].merge(styles["ruled"]) if component.table_style.ruled else styles["header"]
        for index, column in enumerate(component.columns):
            engine.sheet.write(region.row, region.column + index, header_text(column, "\n"), style.merge(Style(text_align=column.header_align or column.align)))
        if component.table_style.repeat_header:
            engine.sheet.repeat_rows(region.row)
        engine.sheet.set_row_height(region.row, 32 if any(column.subtitle for column in component.columns) else 18)
        return 1

    def render_row(self, component, table_row, index, engine, region, styles, occupied):
        """
        Write one prepared row, merging cells that span columns or rows.
        """
        row_style = self.get_row_style(component, table_row, index, styles)
        for column, entry, colspan, rowspan in place_cells(get_entries(component, table_row), region.column, region.row, occupied):
            value, cell_style, cell_format = prepare_entry(entry, engine)
            engine.sheet.write(region.row, column, value, row_style.merge(cell_style), cell_format)
            engine.sheet.merge(region.row, column, colspan, rowspan)

    @staticmethod
    def get_row_style(component, table_row, index, styles):
        """
        Combine the table, striping, row kind and row styles.
        """
        table_style = component.table_style
        style = styles["cell"].merge(styles["bordered"]) if table_style.bordered else styles["cell"]
        if table_style.striped and table_row.kind == "data" and index % 2:
            style = style.merge(styles["stripe"])
        if table_style.compact:
            style = style.merge(styles["compact"])
        if table_style.ruled and table_row.kind == "total":
            style = style.merge(styles["ruled"])
        return style.merge(styles[table_row.kind]).merge(table_row.style)

    @staticmethod
    def set_widths(component, engine, region):
        """
        Size the table columns from their declared widths or titles.
        """
        for index, column in enumerate(component.columns):
            engine.sheet.set_column_width(region.column + index, width_characters(column))


class TableDataRenderer:
    """
    Render a Table in the data mode: its own sheet with one header row, typed values, frozen header and AutoFilter.
    """

    def render(self, component, context, engine):
        """
        Stream the rows to a new sheet without loading them in memory.
        """
        sheet, styles, occupied = engine.table_sheet(component), table_styles(), set()
        for index, column in enumerate(component.columns, start=1):
            sheet.set_column_width(index, width_characters(column))
        sheet.freeze_header()
        sheet.append([(header_text(column, " / "), styles["header"], None) for column in component.columns])
        for row_number, table_row in enumerate(component.rows, start=2):
            TableValidator.validate_row(table_row)
            sheet.append(self.prepare_row(component, table_row, row_number, engine, occupied))
        sheet.add_filter()
        if component.footer:
            sheet.append(self.prepare_row(component, component.footer, sheet.rows + 1, engine, occupied))

    @staticmethod
    def prepare_row(component, table_row, row_number, engine, occupied):
        """
        Lay the row out on columns; spanned positions stay empty because data sheets do not merge cells.
        """
        weight = Style(font_weight=700) if table_row.kind != "data" else Style()
        placed = {column: prepare_entry(entry, engine) for column, entry, colspan, rowspan in place_cells(get_entries(component, table_row), 1, row_number, occupied)}
        return [(placed[column][0], weight, placed[column][2]) if column in placed else (None, Style(), None) for column in range(1, max(placed, default=0) + 1)]


def get_entries(component, table_row):
    """
    Pair each value or explicit cell with its column definition (None for explicit cells).
    """
    if table_row.cells is not None:
        return [(cell, None) for cell in table_row.cells]
    return [(table_row.values.get(column.key), column) for column in component.columns]


def place_cells(entries, start, row, occupied):
    """
    Yield (column, entry, colspan, rowspan), skipping positions held by earlier row spans.
    """
    column = start
    for entry in entries:
        while (row, column) in occupied:
            occupied.discard((row, column))
            column += 1
        colspan, rowspan = (entry[0].colspan, entry[0].rowspan) if isinstance(entry[0], TableCell) else (1, 1)
        occupied.update((row + offset, column + shift) for offset in range(1, rowspan) for shift in range(colspan))
        yield column, entry, colspan, rowspan
        column += colspan


def prepare_entry(entry, engine):
    """
    Return the Excel value, cell style and number format of one entry.
    """
    content, column = entry
    align = Style(text_align=column.align) if column else Style()
    if not isinstance(content, TableCell):
        return engine.value(content), align, number_format(column)
    cell_align = Style(text_align=content.align) if content.align else align
    if content.children:
        return "\n".join(component_text(child) for child in content.children), cell_align.merge(content.style), None
    return engine.value(content.value), cell_align.merge(content.style), number_format(column)


def header_text(column, separator):
    """
    Join a column title and subtitle.
    """
    return f"{column.title}{separator}{column.subtitle}" if column.subtitle else column.title


def width_characters(column):
    """
    Convert a declared column width into Excel characters, or estimate it from the header.
    """
    width = column.width or ""
    if width.endswith("%"):
        return round(float(width[:-1]) * 1.1, 1)
    if width.endswith("px"):
        return round(float(width[:-2]) / 7, 1)
    if width.endswith("mm"):
        return round(float(width[:-2]) * 0.55, 1)
    return min(40, max(10, len(column.title), len(column.subtitle or "")) + 4)
