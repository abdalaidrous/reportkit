from .....styles.borders import edge_borders
from .columns import layout_cell, layout_table


class StackRenderer:
    """
    Render a container's children one below the other; a container with a border or background is framed in a
    one-cell table, like the HTML box.
    """

    def render(self, component, context, engine, area):
        """
        Render the children in the area, or inside a frame when the component is decorated.
        """
        style = context.resolve_style(component)
        target = self.get_frame(engine, area, style) if style.background_color or any(edge_borders(style)) else area
        for child in component.children:
            engine.render(child, context, target)

    @staticmethod
    def get_frame(engine, area, style):
        """
        Return the area of a one-cell table carrying the component border and background.
        """
        table = layout_table(engine, area, [1], style)
        return layout_cell(area, table.add_row().cells[0], 1, style.background_color)


class HeaderRenderer(StackRenderer):
    """
    Render a Header: a repeated one goes to the Word page header, otherwise it stays in the body.
    """

    def render(self, component, context, engine, area):
        """
        Pick the page header for a repeated header.
        """
        super().render(component, context, engine, engine.header() if component.repeat else area)


class FooterRenderer(StackRenderer):
    """
    Render a Footer: a repeated one goes to the Word page footer, otherwise it stays in the body.
    """

    def render(self, component, context, engine, area):
        """
        Pick the page footer for a repeated footer.
        """
        super().render(component, context, engine, engine.footer() if component.repeat else area)
