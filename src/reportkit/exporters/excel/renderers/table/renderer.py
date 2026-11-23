from .....rendering.table import get_entries, header_text, place_cells
from .....styles.style import Style
from .....styles.table import get_header_style, get_row_style, table_styles
from .....styles.tokens import token
from .....validators.table.table import TableValidator
from ...exceptions import ExcelExportError
from .cells import prepare_entry
from .widths import get_widths, spans


class TableRenderer:
    """
    Render a Table in the formatted mode: caption, header, prepared rows and footer, sized and framed like the PDF.
    """

    def render(self, component, context, engine, region):
        """
        Write the table rows in the order they arrive and return the rows used.
        """
        styles = table_styles(context.resolve_style(component))
        widths = get_widths(component, engine, region)
        occupied = set()
        row = region.row

        row += self.render_caption(component, context, engine, region)
        row += self.render_header(component, engine, region.below(row - region.row), styles, widths)

        for index, table_row in enumerate(component.rows):
            TableValidator.validate_row(table_row)
            row += self.render_row(component, table_row, index, engine, region.below(row - region.row), styles, widths, occupied)

        if component.footer:
            TableValidator.validate_row(component.footer)
            row += self.render_row(component, component.footer, 0, engine, region.below(row - region.row), styles, widths, occupied)

        if not component.table_style.ruled:
            engine.sheet.outline(region.row, region.column, sum(widths), row - region.row, styles["frame"])

        return row - region.row

    def render_caption(self, component, context, engine, region):
        """
        Write the table caption across the region when the table has one.
        """
        if not component.header:
            return 0

        style = Style(font_weight=700, font_size=token("--rk-font-lg")).merge(context.resolve_style(component))
        engine.sheet.place(region.row, region.column, region.width, component.header, style)
        return 1

    def render_header(self, component, engine, region, styles, widths):
        """
        Write the column titles and subtitles, repeated on printed pages when requested.
        """
        if not component.table_style.show_header:
            return 0

        style = get_header_style(component, styles)

        for column, (start, width) in zip(component.columns, spans(region, widths)):
            header_style = style.merge(Style(text_align=column.header_align or column.align))
            engine.sheet.place(region.row, start, width, header_text(column, "\n"), header_style, padding=10)

        if component.table_style.repeat_header:
            engine.sheet.repeat_rows(region.row)

        return 1

    def render_row(self, component, table_row, index, engine, region, styles, widths, occupied):
        """
        Write one prepared row, merging cells that span columns or rows, and return the single row it starts.
        """
        row_style = get_row_style(component, table_row, index, styles)
        starts = spans(region, widths)
        column_count = len(widths)

        for column, entry, colspan, rowspan in place_cells(get_entries(component, table_row), 0, region.row, occupied):
            if column < 0 or colspan < 1 or rowspan < 1 or column + colspan > column_count:
                raise ExcelExportError(f"A table cell exceeds the table's {column_count} columns or has an invalid span.")

            value, cell_style, cell_format = prepare_entry(entry, engine)
            width = sum(widths[column:column + colspan])
            engine.sheet.place(region.row, starts[column][0], width, value, row_style.merge(cell_style), cell_format, height=rowspan, padding=10)

        return 1
