from .base import BaseExporter


class ExporterRegistry:
    """
    Register and resolve report exporters by format.
    """

    _exporters: dict[str, type[BaseExporter]] = {}

    @classmethod
    def register(cls, format: str, exporter: type[BaseExporter]):
        """
        Register an exporter for a specific format.
        """
        if not isinstance(format, str) or not format:
            raise ValueError("Exporter format must be a non-empty string.")

        if not isinstance(exporter, type) or not issubclass(exporter, BaseExporter):
            raise TypeError("Exporter must inherit from BaseExporter.")

        if format in cls._exporters:
            raise ValueError(f"Exporter '{format}' is already registered.")

        cls._exporters[format] = exporter
        return exporter

    @classmethod
    def get(cls, format: str) -> type[BaseExporter]:
        """
        Resolve a registered exporter.
        """
        try:
            return cls._exporters[format]
        except KeyError:
            raise ValueError(f"Unknown exporter format: '{format}'.") from None

    @classmethod
    def unregister(cls, format: str):
        """
        Remove a registered exporter.
        """
        cls._exporters.pop(format, None)

    @classmethod
    def all(cls) -> dict[str, type[BaseExporter]]:
        """
        Return all registered exporters.
        """
        return cls._exporters.copy()
