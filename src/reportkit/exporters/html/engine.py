from ...core.component import Component
from ...rendering.context import RenderingContext
from .registry import HtmlRendererRegistry
from .renderers.base import BaseHtmlRenderer
from .styles import HtmlStyleResolver
from .templates import HtmlTemplateEngine


class HtmlRenderingEngine:
    """
    Coordinate HTML rendering using registered component renderers.
    """

    def __init__(self, registry=None, templates=None, styles=None, defer_page_count=False):
        """
        Initialize shared HTML rendering services; defer_page_count lays PageCount out hidden, for PDF chunks whose
        page total is only known once they are merged.
        """
        self.registry = registry if registry is not None else HtmlRendererRegistry
        self.templates = templates if templates is not None else HtmlTemplateEngine()
        self.styles = styles if styles is not None else HtmlStyleResolver()
        self.defer_page_count = defer_page_count

    def render(self, component: Component, context: RenderingContext) -> str:
        """
        Render a component using its registered HTML renderer.
        """
        if not isinstance(component, Component):
            raise TypeError("Expected a Component instance.")

        if not isinstance(context, RenderingContext):
            raise TypeError("Expected a RenderingContext instance.")

        renderer_class = self.registry.get(type(component))

        if not issubclass(renderer_class, BaseHtmlRenderer):
            raise TypeError(f"Invalid HTML renderer for '{type(component).__name__}'.")

        return renderer_class().render(component, context, self)
