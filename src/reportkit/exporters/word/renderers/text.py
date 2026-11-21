from ....components.typography import Heading, RichText
from ....styles.style import Style
from ....styles.tokens import token
from ..styles.text import add_run, format_paragraph, write_paragraph
from ..values import component_text

HEADING_SIZES = {1: "--rk-font-2xl", 2: "--rk-font-xl", 3: "--rk-font-lg"}


class TextRenderer:
    """
    Render Text and Heading as one paragraph, and RichText as one paragraph of styled runs.
    """

    def render(self, component, context, engine, area):
        """
        Write the paragraph into the area.
        """
        style = self.get_style(component, context)
        if isinstance(component, RichText):
            return self.render_spans(component, area.paragraph(), style, engine.direction)
        write_paragraph(area.paragraph(), component_text(component), style, engine.direction)

    def render_spans(self, component, paragraph, style, direction):
        """
        Write each RichText span as its own run with its style and direction.
        """
        format_paragraph(paragraph, style.merge(Style(text_align=component.align)), direction)
        for span in component.spans:
            add_run(paragraph, span.value, style.merge(span.style), span.direction if span.direction in ("ltr", "rtl") else direction)

    @staticmethod
    def get_style(component, context):
        """
        Use the component style, with the heading defaults for headings.
        """
        style = context.resolve_style(component)
        if isinstance(component, Heading):
            return Style(font_weight=700, font_size=token(HEADING_SIZES.get(component.level, "--rk-font-md"))).merge(style)
        return style
