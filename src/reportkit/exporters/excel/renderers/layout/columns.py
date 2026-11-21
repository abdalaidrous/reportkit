from .....rendering.tracks import track_shares


class ColumnsRenderer:
    """
    Render children side by side in bands of slots, like the HTML grid and flex rows.
    """

    def render(self, component, context, engine, region):
        """
        Render the children band by band and return the rows used.
        """
        shares, height = self.get_shares(component, engine), 0
        for start in range(0, len(component.children), len(shares)):
            slots = region.below(height).split(shares)
            height += max(engine.render(child, context, slot) for child, slot in zip(component.children[start:start + len(shares)], slots))
        return height

    def get_shares(self, component, engine):
        """
        Give every child of a row an equal share.
        """
        return [1] * max(1, len(component.children))


class GridRenderer(ColumnsRenderer):
    """
    Render a Grid with its column tracks (fr, auto, %, px).
    """

    def get_shares(self, component, engine):
        """
        Convert the grid tracks into width shares.
        """
        tracks = ["1fr"] * component.columns if isinstance(component.columns, int) else component.columns.split()
        return track_shares(tracks, engine.sheet.content_pixels)


class InfoGridRenderer(ColumnsRenderer):
    """
    Render an InfoGrid with its configured number of equal columns.
    """

    def get_shares(self, component, engine):
        """
        Give every column an equal share.
        """
        return [1] * component.columns
