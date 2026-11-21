from ....components.document import Footer, Header


class RunningElementResolver:
    """
    Build CSS for repeating headers and footers.
    """

    ELEMENTS = {Header: ("rk-running-header", "top-center"), Footer: ("rk-running-footer", "bottom-center")}

    @classmethod
    def name(cls, component):
        """
        Return the running element name.
        """
        return cls.ELEMENTS[type(component)][0]

    @classmethod
    def position(cls, component):
        """
        Return the page margin position.
        """
        return cls.ELEMENTS[type(component)][1]

    @classmethod
    def resolve(cls, components):
        """
        Build the running element rules.
        """
        return "\n".join(f".{cls.name(component)} {{ position: running({cls.name(component)}); }}" for component in components)
