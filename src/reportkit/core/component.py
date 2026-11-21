from dataclasses import dataclass, field

from ..styles.style import Style


@dataclass(kw_only=True)
class Component:
    """
    Base class for all report components.
    """

    style: Style = field(default_factory=Style)
