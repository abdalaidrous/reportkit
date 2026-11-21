from ..exceptions import ExcelExportError


class ExcelRendererRegistry:
    """
    Map component classes to the Excel renderer used for them in one presentation mode.
    """

    def __init__(self, renderers):
        """
        Keep the component to renderer mapping.
        """
        self.renderers = dict(renderers)

    def get(self, component):
        """
        Return the renderer for a component, or fail clearly when the mode cannot show it.
        """
        try:
            return self.renderers[type(component)]
        except KeyError:
            raise ExcelExportError(f"{type(component).__name__} is not supported by the Excel exporter in this mode.") from None
