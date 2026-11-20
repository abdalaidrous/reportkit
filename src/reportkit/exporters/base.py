from abc import ABC, abstractmethod

from ..core.component import Component
from ..rendering.context import RenderingContext


class BaseExporter(ABC):
    """
    Define the shared contract for report exporters.
    """

    @abstractmethod
    def export(self, document: Component, context: RenderingContext) -> bytes:
        """
        Export a report document into its target format.
        """
        raise NotImplementedError
