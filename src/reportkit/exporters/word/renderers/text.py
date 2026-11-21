from ....components.typography import Heading, RichText
from ....styles.style import Style
from ....styles.tokens import token
from ..styles.text import add_run, format_paragraph, write_paragraph
from ..values import component_text


HEADING_SIZES = {1: "--rk-font-2xl", 2: "--rk-font-xl", 3: "--rk-font-lg"}


class TextRenderer:
    """
    Render Text, Heading, and RichText components.
    """

    def render(self, component, context, engine, area):
        """
        Render the component with its resolved style.
        """
        style = self.get_style(component, context)

        if isinstance(component, RichText):
            return self.render_spans(component, area, style, engine.direction)

        self.render_text(component, area, style, engine.direction)

    @staticmethod
    def render_text(component, area, style, direction):
        """
        Render a text or heading paragraph.
        """
        write_paragraph(area.paragraph(), component_text(component), style, direction)

    def render_spans(self, component, area, style, direction):
        """
        Render rich text spans with their individual styles.
        """
        paragraph = area.paragraph()
        self.format_spans(paragraph, component, style, direction)

        for span in component.spans:
            self.render_span(paragraph, span, style, direction)

    @staticmethod
    def format_spans(paragraph, component, style, direction):
        """
        Format the rich text paragraph.
        """
        format_paragraph(paragraph, style.merge(Style(text_align=component.align)), direction)

    @staticmethod
    def render_span(paragraph, span, style, direction):
        """
        Render a single rich text span.
        """
        span_style = style.merge(span.style)
        span_direction = span.direction if span.direction in ("ltr", "rtl") else direction
        add_run(paragraph, span.value, span_style, span_direction)

    @classmethod
    def get_style(cls, component, context):
        """
        Resolve the component style with heading defaults.
        """
        style = context.resolve_style(component)

        if isinstance(component, Heading):
            return cls.get_heading_style(component, style)

        return style

    @staticmethod
    def get_heading_style(component, style):
        """
        Apply the default heading font size and weight.
        """
        font_size = token(HEADING_SIZES.get(component.level, "--rk-font-md"))
        return Style(font_weight=700, font_size=font_size).merge(style)