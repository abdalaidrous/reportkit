from ...core.component import Component


class HtmlRendererRegistry:
    """
    Register and resolve HTML component renderers.
    """

    _renderers: dict[type[Component], type] = {}

    @classmethod
    def register(cls, component: type[Component], renderer: type):
        """
        Register an HTML renderer for a component.
        """
        if not isinstance(component, type) or not issubclass(component, Component):
            raise TypeError("Component must inherit from Component.")

        if not isinstance(renderer, type):
            raise TypeError("Renderer must be a class.")

        if component in cls._renderers:
            raise ValueError(f"Renderer for '{component.__name__}' is already registered.")

        cls._renderers[component] = renderer
        return renderer

    @classmethod
    def get(cls, component: type[Component]) -> type:
        """
        Resolve the registered HTML renderer.
        """
        try:
            return cls._renderers[component]
        except KeyError:
            raise ValueError(
                f"No HTML renderer registered for '{component.__name__}'."
            ) from None

    @classmethod
    def all(cls) -> dict[type[Component], type]:
        """
        Return all registered HTML renderers.
        """
        return cls._renderers.copy()
