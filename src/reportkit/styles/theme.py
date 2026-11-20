from dataclasses import dataclass, field

from .style import Style


@dataclass
class Theme:
    """
    Manage named reusable styles for report components.
    """

    name: str = "default"
    styles: dict[str, Style] = field(default_factory=dict)

    def register(self, name: str, style: Style):
        """
        Register a named style.
        """
        if not isinstance(name, str) or not name:
            raise ValueError("Style name must be a non-empty string.")

        if not isinstance(style, Style):
            raise TypeError("Expected a Style instance.")

        if name in self.styles:
            raise ValueError(f"Style '{name}' is already registered.")

        self.styles[name] = style
        return self

    def get(self, name: str) -> Style:
        """
        Resolve a registered style.
        """
        try:
            return self.styles[name]
        except KeyError:
            raise ValueError(f"Unknown style: '{name}'.") from None

    def resolve(self, name: str, override: Style | None = None) -> Style:
        """
        Resolve a named style with optional overrides.
        """
        style = self.get(name)
        return style.merge(override) if override is not None else style
