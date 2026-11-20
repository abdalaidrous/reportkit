import json
from dataclasses import fields, is_dataclass

from ..styles.style import Style
from .component import Component
from .factory import ComponentFactory
from .registry import ComponentRegistry


class ComponentSerializer:
    """
    Serialize and restore report component trees.
    """

    @classmethod
    def to_dict(cls, component: Component) -> dict:
        """
        Convert a component tree into a dictionary.
        """
        if not isinstance(component, Component):
            raise TypeError("Expected a Component instance.")

        component_type = cls.resolve_type(component)
        data = {"type": component_type}

        for field in fields(component):
            value = getattr(component, field.name)
            data[field.name] = cls.serialize_value(value)

        return data

    @classmethod
    def serialize_value(cls, value):
        """
        Serialize nested components and supported values.
        """
        if isinstance(value, Style):
            return value.to_dict()

        if isinstance(value, Component):
            return cls.to_dict(value)

        if isinstance(value, list):
            return [cls.serialize_value(item) for item in value]

        if isinstance(value, tuple):
            return [cls.serialize_value(item) for item in value]

        if isinstance(value, dict):
            return {key: cls.serialize_value(item) for key, item in value.items()}

        if is_dataclass(value) and not isinstance(value, type):
            return {
                field.name: cls.serialize_value(getattr(value, field.name))
                for field in fields(value)
            }

        return value

    @staticmethod
    def resolve_type(component: Component) -> str:
        """
        Resolve the registered name of a component.
        """
        for name, component_class in ComponentRegistry.all().items():
            if type(component) is component_class:
                return name

        raise ValueError(f"Component '{type(component).__name__}' is not registered.")

    @classmethod
    def to_json(cls, component: Component, **kwargs) -> str:
        """
        Serialize a component tree into JSON.
        """
        return json.dumps(cls.to_dict(component), ensure_ascii=False, **kwargs)

    @staticmethod
    def from_dict(data: dict) -> Component:
        """
        Build a component tree from a dictionary.
        """
        return ComponentFactory.create(data)

    @classmethod
    def from_json(cls, data: str) -> Component:
        """
        Build a component tree from JSON.
        """
        return cls.from_dict(json.loads(data))
