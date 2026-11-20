from abc import ABC, abstractmethod

from ..core.component import Component, Container
from ..core.registry import ComponentRegistry
from .context import RenderingContext


class ComponentVisitor(ABC):
    """
    Visit report components using registered component types.
    """

    def visit(self, component: Component, context: RenderingContext):
        """
        Dispatch a component to its matching visitor method.
        """
        if not isinstance(component, Component):
            raise TypeError("Expected a Component instance.")

        component_type = self.resolve_type(component)

        method = getattr(self, f"visit_{component_type}", None)

        if method is None:
            return self.visit_default(component, context)

        return method(component, context)

    def visit_children(self, container: Container, context: RenderingContext):
        """
        Visit all child components in their original order.
        """
        if not isinstance(container, Container):
            raise TypeError("Expected a Container instance.")

        return [self.visit(child, context) for child in container.children]

    @staticmethod
    def resolve_type(component: Component) -> str:
        """
        Resolve the registered type of a component.
        """
        for name, component_class in ComponentRegistry.all().items():
            if type(component) is component_class:
                return name

        raise ValueError(f"Component '{type(component).__name__}' is not registered.")

    @abstractmethod
    def visit_default(self, component: Component, context: RenderingContext):
        """
        Handle components without a specialized visitor method.
        """
        raise NotImplementedError
