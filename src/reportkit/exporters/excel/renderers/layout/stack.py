class StackRenderer:
    """
    Render a container's children one below the other.
    """

    def render(self, component, context, engine, region):
        """
        Render each child under the previous one and return the rows used.
        """
        height = 0
        for child in component.children:
            height += engine.render(child, context, region.below(height))
        return height
