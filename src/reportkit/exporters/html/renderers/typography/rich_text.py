from ..base import BaseHtmlRenderer


class RichTextRenderer(BaseHtmlRenderer):
    """Render styled text fragments into HTML."""

    template_name = "components/typography/rich_text.html"

    def render(self, component, context, engine):
        """Render rich text with independently styled spans."""
        style = engine.styles.resolve(context.resolve_style(component))
        spans = [self.prepare_span(span, engine) for span in component.spans]
        return engine.templates.render(self.template_name, spans=spans, align=component.align, style=style)

    def prepare_span(self, span, engine):
        """Prepare one text fragment for rendering."""
        return {
            "value": span.value,
            "style": engine.styles.resolve(span.style),
            "language": span.language,
            "direction": span.direction,
        }
