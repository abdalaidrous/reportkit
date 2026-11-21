from pathlib import Path

from reportkit.components import Column, Heading, Report, Row, Section, Text
from reportkit.components.layout import Divider, Grid, Spacer
from reportkit.components.table import Table, TableColumn
from reportkit.exporters.registry import ExporterRegistry
from reportkit.rendering.context import RenderingContext
from reportkit.styles.style import Style
import reportkit.exporters.html


OUTPUT_DIR = Path(__file__).parent / "output"


def build_report():
    """
    Build a styled financial HTML report example.
    """
    card_style = Style(
        background_color="#ffffff",
        padding=24,
        border_width=1,
        border_style="solid",
        border_color="#e2e8f0",
        border_radius=12,
        flex=1,
        gap=8,
        box_shadow="0 4px 12px rgba(15, 23, 42, 0.06)",
    )

    return Report(
        title="التقرير المالي",
        children=[
            Section(
                style=Style(margin_bottom=32),
                children=[
                    Heading("التقرير المالي", level=1, style=Style(font_size=30, font_weight=700, color="#1e3a8a")),
                    Text("تقرير الحركة المالية لشهر نوفمبر 2026", style=Style(font_size=14, color="#64748b")),
                    Text("الفترة: 01 نوفمبر 2026 - 20 نوفمبر 2026", style=Style(font_size=12, color="#94a3b8")),
                ],
            ),
            Section(
                style=Style(margin_bottom=32),
                children=[
                    Heading("الملخص المالي", level=2, style=Style(font_size=22, color="#0f172a")),
                    Row(
                        style=Style(gap=16),
                        children=[
                            Column(children=[Text("إجمالي المقبوضات", style=Style(color="#64748b", font_size=13)), Heading("15,000 ر.س", level=2, style=Style(font_size=26, color="#059669")), Text("المبالغ المستلمة خلال الفترة", style=Style(color="#94a3b8", font_size=12))], style=card_style),
                            Column(children=[Text("إجمالي المصروفات", style=Style(color="#64748b", font_size=13)), Heading("8,000 ر.س", level=2, style=Style(font_size=26, color="#dc2626")), Text("المبالغ المصروفة خلال الفترة", style=Style(color="#94a3b8", font_size=12))], style=card_style),
                            Column(children=[Text("صافي الحركة", style=Style(color="#64748b", font_size=13)), Heading("7,000 ر.س", level=2, style=Style(font_size=26, color="#2563eb")), Text("الفرق بين المقبوضات والمصروفات", style=Style(color="#94a3b8", font_size=12))], style=card_style),
                        ],
                    ),
                ],
            ),
            Section(
                style=Style(margin_bottom=32),
                children=[
                    Heading("تفاصيل الحركة المالية", level=2, style=Style(font_size=22, color="#0f172a")),
                    Row(
                        style=Style(gap=16, margin_bottom=12),
                        children=[
                            Column(children=[Text("سند قبض REC-001", style=Style(font_weight=700)), Text("طريقة الدفع: نقدًا", style=Style(color="#64748b"))], style=Style(flex=1)),
                            Column(children=[Text("15,000 ر.س", style=Style(color="#059669", font_weight=700)), Text("تم الاستلام في 20 نوفمبر 2026", style=Style(color="#64748b"))], style=Style(flex=1)),
                        ],
                    ),
                    Row(
                        style=Style(gap=16),
                        children=[
                            Column(children=[Text("سند صرف PAY-001", style=Style(font_weight=700)), Text("طريقة الدفع: تحويل بنكي", style=Style(color="#64748b"))], style=Style(flex=1)),
                            Column(children=[Text("8,000 ر.س", style=Style(color="#dc2626", font_weight=700)), Text("تم الصرف في 19 نوفمبر 2026", style=Style(color="#64748b"))], style=Style(flex=1)),
                        ],
                    ),
                ],
            ),
            Section(
                children=[
                    Heading(value="ملخص الحسابات المالية", level=2),
                    Spacer(height=20),
                    Grid(
                        columns=3,
                        style=Style(gap=16),
                        children=[
                            Column(
                                style=Style(padding=20, background_color="#f8fafc", border_radius=10),
                                children=[
                                    Text(value="الصندوق الرئيسي"),
                                    Heading(value="25,000 ر.س", level=3),
                                ],
                            ),
                            Column(
                                style=Style(padding=20, background_color="#f8fafc", border_radius=10),
                                children=[
                                    Text(value="البنك الأهلي"),
                                    Heading(value="80,000 ر.س", level=3),
                                ],
                            ),
                            Column(
                                style=Style(padding=20, background_color="#f8fafc", border_radius=10),
                                children=[
                                    Text(value="حساب التسوية"),
                                    Heading(value="12,000 ر.س", level=3),
                                ],
                            ),
                        ],
                    ),
                    Divider(style=Style(margin_top=24, margin_bottom=24)),
                    Text(value="جميع المبالغ بالريال السعودي."),
                ],
            ),
            Section(
                children=[
                    Heading(value="تفاصيل العمليات المالية", level=2),
                    Table(
                        columns=[
                            TableColumn(key="date", title="التاريخ", width="130px"),
                            TableColumn(key="reference", title="رقم العملية"),
                            TableColumn(key="description", title="البيان"),
                            TableColumn(key="type", title="النوع"),
                            TableColumn(key="amount", title="المبلغ", align="end"),
                        ],
                        rows=[
                            {"date": "2026-11-01", "reference": "REC-001", "description": "سند قبض نقدي", "type": "قبض", "amount": 5000},
                            {"date": "2026-11-02", "reference": "PAY-001", "description": "مصروفات تشغيل", "type": "صرف", "amount": -2000},
                            {"date": "2026-11-03", "reference": "REC-002", "description": "تحويل بنكي", "type": "قبض", "amount": 7000},
                            {"date": "2026-11-04", "reference": "PAY-002", "description": "مصاريف صيانة", "type": "صرف", "amount": -1500},
                        ],
                    ),
                ],
            ),
        ],
    )


def main():
    """
    Generate the styled financial HTML report.
    """
    context = RenderingContext(language="ar", direction="rtl")
    exporter = ExporterRegistry.get("html")()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / "report.html"
    output.write_bytes(exporter.export(build_report(), context))
    print(f"Report generated: {output.resolve()}")


if __name__ == "__main__":
    main()
