from dataclasses import dataclass, field

from ..styles.style import Style


@dataclass(kw_only=True)
class Component:
    """
    Base class for all report components.
    """

    style: Style = field(default_factory=Style)


@dataclass
class Container(Component):
    """
    Base component for managing nested report components.
    """

    children: list[Component] = field(default_factory=list)

    def __post_init__(self):
        """
        Validate and initialize child components.
        """
        children = self.children
        self.children = []
        self.extend(children)

    def add(self, component: Component):
        """
        Add a validated child component.
        """
        self._validate_child(component)
        self.children.append(component)
        return self

    def extend(self, components: list[Component]):
        """
        Add multiple validated child components.
        """
        components = list(components)

        for component in components:
            self._validate_child(component)

        self.children.extend(components)
        return self

    def _validate_child(self, component: Component):
        """
        Validate child type and prevent circular references.
        """
        if not isinstance(component, Component):
            raise TypeError("Child must be a Component.")

        if component is self:
            raise ValueError("A container cannot contain itself.")

        if isinstance(component, Container) and component._contains(self):
            raise ValueError("Circular component references are not allowed.")

    def _contains(self, target: Component):
        """
        Check whether a component exists in the descendant tree.
        """
        visited = set()
        stack = list(self.children)

        while stack:
            component = stack.pop()

            if component is target:
                return True

            if id(component) in visited:
                continue

            visited.add(id(component))

            if isinstance(component, Container):
                stack.extend(component.children)

        return False
