from abc import ABC, abstractmethod


class BaseHtmlRenderer(ABC):
    """
    Define the base contract for HTML component renderers.
    """

    @abstractmethod
    def render(self, component, context, engine) -> str:
        """
        Render a component into HTML.
        """
        raise NotImplementedError

    def render_children(self, component, context, engine) -> str:
        """
        Render nested components using the HTML rendering engine.
        """
        return "".join(engine.render(child, context) for child in component.children)
