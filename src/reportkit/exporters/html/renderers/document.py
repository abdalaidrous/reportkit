from .base import BaseHtmlRenderer


class ReportRenderer(BaseHtmlRenderer):
    """
    Render the root report container.
    """

    template_name = "components/report.html"

    def render(self, component, context, engine) -> str:
        """
        Render the report and all nested components.
        """
        children = self.render_children(component, context, engine)
        return engine.templates.render(self.template_name, children=children)
