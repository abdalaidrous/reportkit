from ..exceptions import WordExportError


class WordRendererRegistry:
    """
    Map component classes to the Word renderer used for them.
    """

    def __init__(self, renderers):
        """
        Keep the component to renderer mapping.
        """
        self.renderers = dict(renderers)

    def get(self, component):
        """
        Return the renderer for a component, or fail clearly when Word export cannot show it.
        """
        try:
            return self.renderers[type(component)]
        except KeyError:
            raise WordExportError(f"{type(component).__name__} is not supported by the Word exporter.") from None
