from ..core.component import Component


class ComponentRegistry:
    """
    Register and resolve report component types.
    """

    _components: dict[str, type[Component]] = {}

    @classmethod
    def register(cls, name: str, component: type[Component]):
        """
        Register a component type.
        """
        if not isinstance(name, str) or not name:
            raise ValueError("Component name must be a non-empty string.")

        if not isinstance(component, type) or not issubclass(component, Component):
            raise TypeError("Registered component must inherit from Component.")

        if name in cls._components:
            raise ValueError(f"Component '{name}' is already registered.")

        cls._components[name] = component
        return component

    @classmethod
    def get(cls, name: str) -> type[Component]:
        """
        Resolve a registered component type.
        """
        try:
            return cls._components[name]
        except KeyError:
            raise ValueError(f"Unknown component type: '{name}'.") from None

    @classmethod
    def unregister(cls, name: str):
        """
        Remove a registered component type.
        """
        cls._components.pop(name, None)

    @classmethod
    def all(cls) -> dict[str, type[Component]]:
        """
        Return all registered component types.
        """
        return cls._components.copy()
