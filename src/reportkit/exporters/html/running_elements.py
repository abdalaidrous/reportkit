from ...components.document import Footer, Header


class RunningElementResolver:
    """Resolve repeating page elements."""

    ELEMENTS = {
        Header: ("rk-running-header", "top-center"),
        Footer: ("rk-running-footer", "bottom-center"),
    }

    @classmethod
    def resolve(cls, document):
        """Build CSS for repeating page elements."""
        components = cls.find_components(document)
        cls.validate(components)
        rules = []
        for component in components:
            name, _ = cls.ELEMENTS[type(component)]
            rules.append(f".{name} {{ position: running({name}); }}")
        return "\n".join(rules)

    @classmethod
    def find_components(cls, component):
        """Find repeating headers and footers."""
        result = []
        if type(component) in cls.ELEMENTS and component.repeat:
            result.append(component)
        for child in getattr(component, "children", []):
            result.extend(cls.find_components(child))
        return result

    @classmethod
    def validate(cls, components):
        """Validate unique running elements."""
        types = [type(component) for component in components]
        if len(types) != len(set(types)):
            raise ValueError("Only one repeating Header and Footer are supported.")
