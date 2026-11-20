from dataclasses import dataclass, field

from ..core.component import Component
from ..styles.style import Style
from ..styles.theme import Theme


@dataclass
class RenderingContext:
    """
    Manage shared rendering settings and component styles.
    """
    language: str = "en"
    direction: str = "ltr"
    theme: Theme = field(default_factory=Theme)

    def resolve_style(self, component: Component, style_name: str | None = None) -> Style:
        """
        Resolve the final style for a component.
        """
        if not isinstance(component, Component):
            raise TypeError("Expected a Component instance.")

        style = self.theme.get(style_name) if style_name else Style()
        return style.merge(component.style)

    def with_language(self, language: str, direction: str | None = None) -> "RenderingContext":
        """
        Create a context with updated language settings.
        """
        return RenderingContext(language=language, direction=direction or self.direction, theme=self.theme)