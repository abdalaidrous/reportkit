from collections.abc import Mapping
from dataclasses import fields

from ..styles.style import Style
from .component import Component
from .container import Container
from .registry import ComponentRegistry


class ComponentFactory:
    """
    Create registered report components from dictionaries.
    """

    @classmethod
    def create(cls, data: Mapping) -> Component:
        """
        Create a component from its definition.
        """
        if not isinstance(data, Mapping):
            raise TypeError("Component definition must be a mapping.")

        component_type = data.get("type")
        if not isinstance(component_type, str) or not component_type:
            raise ValueError("Component type must be a non-empty string.")

        component_class = ComponentRegistry.get(component_type)
        properties = {key: value for key, value in data.items() if key != "type"}
        cls.validate_properties(component_class, properties)

        if "style" in properties and not isinstance(properties["style"], Style):
            properties["style"] = Style.from_dict(properties["style"])

        if issubclass(component_class, Container):
            children = properties.get("children", [])
            if not isinstance(children, list):
                raise TypeError("Component children must be a list.")
            properties["children"] = [cls.create(child) for child in children]
        elif "children" in properties:
            raise ValueError(f"Component '{component_type}' does not support children.")

        return component_class(**properties)

    @staticmethod
    def validate_properties(component_class: type[Component], properties: dict):
        """
        Validate component properties against its dataclass fields.
        """
        allowed = {field.name for field in fields(component_class)}
        unknown = set(properties) - allowed

        if unknown:
            raise ValueError( f"Unknown properties for '{component_class.__name__}': {', '.join(sorted(unknown))}")
