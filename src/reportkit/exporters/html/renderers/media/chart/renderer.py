from ......rendering.chart import chart_colors, legend_names
from ......styles.tokens import token
from ...base import BaseHtmlRenderer
from .layout import CartesianLayout, PieLayout


class ChartRenderer(BaseHtmlRenderer):
    """
    Render a chart as inline SVG shapes drawn at export time, with its texts as HTML laid over them, so browsers and
    the PDF show it without scripts and shape Arabic labels correctly.
    """

    template_name = "components/media/chart.html"

    def render(self, component, context, engine):
        """
        Lay the chart out and render its title, drawing and legend.
        """
        style = engine.styles.resolve(context.resolve_style(component))
        colors = chart_colors(component)
        layout = PieLayout(component, colors) if component.chart_type == "pie" else CartesianLayout(component, colors)
        legend = list(zip(legend_names(component), colors)) if component.legend else []
        return engine.templates.render(self.template_name, component=component, layout=layout, legend=legend, style=style, theme=self.theme())

    @staticmethod
    def theme():
        """
        Return the resolved line colors: SVG drawn by WeasyPrint does not read CSS variables.
        """
        return {"axis": token("--rk-chart-axis-color"), "grid": token("--rk-chart-grid-color")}
