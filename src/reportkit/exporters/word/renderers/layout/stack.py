from .....styles.borders import edge_borders
from .columns import layout_cell, layout_table


class StackRenderer:
    """
    Render container children vertically with optional borders and background.
    """

    def render(self, component, context, engine, area):
        """
        Render children inside the container or its decorated frame.
        """
        style = context.resolve_style(component)
        target = self.get_target(engine, area, style)
        self.render_children(component, context, engine, target)

    @classmethod
    def get_target(cls, engine, area, style):
        """
        Resolve the rendering area based on the container decoration.
        """
        return cls.get_frame(engine, area, style) if cls.has_frame(style) else area

    @staticmethod
    def has_frame(style):
        """
        Check whether the container requires a decorated frame.
        """
        return bool(style.background_color or any(edge_borders(style)))

    @staticmethod
    def get_frame(engine, area, style):
        """
        Create a one-cell table for the container border and background.
        """
        table = layout_table(engine, area, [1], style)
        return layout_cell(area, table.add_row().cells[0], 1, style.background_color)

    @staticmethod
    def render_children(component, context, engine, area):
        """
        Render the container children in order.
        """
        for child in component.children:
            engine.render(child, context, area)


class HeaderRenderer(StackRenderer):
    """
    Render header content in the body or repeated page header.
    """

    def render(self, component, context, engine, area):
        """
        Render the header in its configured area.
        """
        target = engine.header() if component.repeat else area
        super().render(component, context, engine, target)


class FooterRenderer(StackRenderer):
    """
    Render footer content in the body or repeated page footer.
    """

    def render(self, component, context, engine, area):
        """
        Render the footer in its configured area.
        """
        target = engine.footer() if component.repeat else area
        super().render(component, context, engine, target)