from ......rendering.chart import chart_colors, legend_names
from ......styles.tokens import token
from ...base import BaseHtmlRenderer
from .layout import CartesianLayout, PieLayout


class ChartRenderer(BaseHtmlRenderer):
    """
    Render a chart as inline SVG drawn at export time, so browsers and the PDF show it without scripts.
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
        Return the resolved chart colors and font: SVG drawn by WeasyPrint does not read CSS variables.
        """
        return {
            "font": token("--rk-font-family"),
            "axis": token("--rk-chart-axis-color"),
            "grid": token("--rk-chart-grid-color"),
            "label": token("--rk-chart-label-color"),
            "size": token("--rk-chart-label-size"),
        }
