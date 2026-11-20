from ....components.text import Text
from ..registry import HtmlRendererRegistry
from .text import TextRenderer


HtmlRendererRegistry.register(Text, TextRenderer)
