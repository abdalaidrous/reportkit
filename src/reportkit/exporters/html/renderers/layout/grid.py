import re
from ..base import BaseHtmlRenderer


GRID_TRACK_PATTERN = re.compile(r"^(?:\d+(?:\.\d+)?(?:fr|px|%|rem|em)|auto|min-content|max-content)$")


class GridRenderer(BaseHtmlRenderer):
    """
    Render report components in a grid layout.
    """

    template_name = "components/layout/grid.html"

    def render(self, component, context, engine):
        """
        Render grid columns and nested components.
        """
        style = context.resolve_style(component)
        columns = self.resolve_columns(component.columns)
        css_class = self.get_class(component.columns, style.direction or context.direction)
        children = self.render_children(component, context, engine)
        return engine.templates.render(self.template_name, children=children, columns=columns, flow=css_class, style=engine.styles.resolve(style))

    @staticmethod
    def resolve_columns(columns):
        """
        Resolve grid column definitions.
        """
        if isinstance(columns, bool):
            raise ValueError("Grid columns must be a positive integer or valid track definition.")
        if isinstance(columns, int):
            if columns < 1:
                raise ValueError("Grid columns must be a positive integer.")
            return f"repeat({columns}, minmax(0, 1fr))"
        if isinstance(columns, str):
            tracks = columns.split()
            if tracks and all(GRID_TRACK_PATTERN.fullmatch(track) for track in tracks):
                return " ".join(tracks)
        raise ValueError("Invalid grid column definition.")

    @staticmethod
    def get_class(columns, direction):
        """
        Get grid direction and column CSS classes.
        """
        count = columns if isinstance(columns, int) else len(columns.split())
        return f"rk-grid--{direction} rk-grid--cols-{count}"