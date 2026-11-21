# ReportKit — دليل المشروع لـ Claude

## الهدف

ReportKit مكتبة Python مستقلة لبناء التقارير من مكونات قابلة لإعادة الاستخدام، ثم تحويلها إلى HTML أو صيغ تصدير أخرى. المكتبة مسؤولة عن بنية التقرير، التنسيق، العرض، الأصول، والطباعة؛ أما البيانات والحسابات والإجماليات فتأتي جاهزة من التطبيق المستدعي.

المشروع لا يعتمد على Django، ولا يجب أن يضيف منطقًا خاصًا بتقرير مالي واحد إلى المكونات العامة.

## مثال التشغيل الحالي

المثال الرئيسي هو تقرير الحركة المالية:

```powershell
pip install -e .
python -m examples.financial_movement.report
```

ينتج الملف:

```text
examples/financial_movement/reportkit_output.html
```

يبني المثال تقريرًا يحتوي على ترويسة فندق ثنائية اللغة، شعار، بيانات تعريفية، فلاتر، جدول حركات، وجدول ملخص. يتم تمرير الصفوف والإجماليات جاهزة، ولا تحسب ReportKit أي إجماليات أو مجاميع.

مثال مبسط:

```python
from reportkit.components.document import Report
from reportkit.components.layout import Grid, Column
from reportkit.components.media import Image
from reportkit.components.typography import Heading, Text
from reportkit.exporters.registry import ExporterRegistry
from reportkit.rendering.context import RenderingContext
import reportkit.exporters.html

report = Report(
    title="Financial Movement Report",
    children=[
        Grid(
            columns="1fr auto 1fr",
            style=Style(direction="ltr"),
            children=[
                Column(children=[Heading(value="Alahqaf Hotel"), Text(value="Saudi Arabia - Khobar")]),
                Image(src="logo.png", alt="Hotel logo", width="80"),
                Column(direction="rtl", align="end", children=[Heading(value="فندق الأحقاف")]),
            ],
        )
    ],
)

exporter = ExporterRegistry.get("html")()
html = exporter.export(report, RenderingContext(language="ar", direction="rtl"))
```

## البنية المعمارية

التدفق الأساسي هو:

```text
Application data
    ↓
Components tree
    ↓
RenderingContext + Theme + Style
    ↓
ExporterRegistry → HtmlExporter
    ↓
HtmlRenderingEngine → RendererRegistry → Jinja2 templates + CSS
    ↓
Complete HTML / printable A4 document
```

### قواعد مهمة

- `Component` هو الأساس، و`Container` يضيف `children` والتحقق من الدورات.
- كل Component يصف البيانات فقط؛ لا يضع HTML داخله.
- كل Renderer مسؤول عن تحويل Component إلى مخرجات العرض.
- `HtmlRendererRegistry` يربط Class المكوّن بـ Renderer الخاص به.
- `Style` كائن قيمة مستقل وغير قابل للتعديل، و`Theme` يوفر تنسيقات مسماة.
- `HtmlStyleResolver` يحول خصائص Style إلى CSS آمن.
- Jinja2 مسؤولة عن القوالب وHTML escaping. لا تستخدم `safe` مع نصوص المستخدم.
- الصور المحلية تُحل عبر `AssetResolver` إلى مسار صالح أو Data URI، بدل الاعتماد على مسار جهاز المطور.
- الجداول تستقبل `TableColumn` و`TableRow` جاهزين. لا تضف حسابات أو تجميعات داخل ReportKit.
- دعم RTL/LTR يكون على مستوى المكوّن أو الحاوية، ولا يغير اتجاه التقرير كاملًا دون طلب.
- التخطيط المطبوع يستهدف A4، مع دعم تكرار رأس الجدول وتجنب تقسيم الصفوف قدر الإمكان.

## شجرة المشروع

```text
reportkit/
├── CLAUDE.md
├── pyproject.toml
├── requirements.txt
├── README.md
├── examples/
│   ├── __init__.py
│   └── financial_movement/
│       ├── __init__.py
│       ├── data.py              # بيانات المثال الجاهزة
│       ├── logo.png             # أصل الشعار المحلي
│       ├── report.py            # بناء وتشغيل التقرير
│       ├── styles.py            # Styles الخاصة بالمثال
│       ├── README.md
│       └── reportkit_output.html
├── src/reportkit/
│   ├── __init__.py
│   ├── report.py
│   ├── core/
│   │   ├── component.py         # Component الأساسي
│   │   ├── container.py         # Container وchildren
│   │   ├── factory.py           # إنشاء الشجرة من dict
│   │   ├── registry.py          # تسجيل أنواع المكونات
│   │   ├── serializer.py        # dict/JSON
│   │   └── exceptions.py
│   ├── components/
│   │   ├── document/            # Report, Page, Header, Footer
│   │   ├── layout/              # Box, Section, Row, Column, Grid...
│   │   ├── typography/          # Text, Heading, RichText
│   │   ├── table/               # Table, TableColumn, TableRow, TableCell
│   │   ├── information/         # KeyValue, InfoGrid
│   │   ├── media/               # Image, Chart
│   │   └── pagination/          # PageBreak, PageNumber, PageCount
│   ├── validators/
│   │   └── table/               # column, cell, row, table: قواعد التحقق خارج المكونات
│   ├── styles/                  # Style وTheme
│   ├── formatting/              # تنسيق القيم البسيطة للعرض فقط (TableCellFormatter)
│   ├── rendering/               # RenderingContext وVisitor الأساسي
│   └── exporters/
│       ├── base.py
│       ├── registry.py
│       ├── html/
│       │   ├── exporter.py
│       │   ├── engine.py
│       │   ├── templates.py
│       │   ├── styles.py
│       │   ├── assets.py
│       │   ├── page/
│       │   │   ├── resolver.py   # HtmlPageResolver: تنسيق إنشاء CSS الطباعة فقط
│       │   │   ├── validator.py  # HtmlPageValidator: كل إعدادات الصفحة المؤثرة في CSS
│       │   │   ├── components.py # HtmlPageComponentFinder: بحث واحد في الشجرة
│       │   │   ├── styles.py     # PageStyleResolver: قاعدة @page
│       │   │   ├── margins.py    # PageMarginRegistry
│       │   │   ├── numbering.py  # PageNumberStyleResolver
│       │   │   └── running.py    # RunningElementResolver
│       │   ├── renderers/        # Renderer مستقل لكل نوع
│       │   │   └── table/        # table.py: الجدول والصفوف، cell.py: الخلايا وchildren
│       │   ├── templates/        # قوالب Jinja2 (table.html + cell.html مشترك بين tbody وtfoot)
│       │   └── static/           # tokens, layout, table, print...
│       ├── pdf/
│       │   ├── exporter.py       # PdfExporter: HtmlExporter ثم PdfConversionService فقط
│       │   ├── conversion.py     # PdfConversionService + WeasyPrintErrorMonitor (مراقبة لكل thread)
│       │   ├── dependencies.py   # تحميل WeasyPrint الاختياري
│       │   ├── exceptions.py     # PdfExportError
│       │   └── resources/        # fetcher.py (URLFetcher لـ WeasyPrint 70) و policy.py (PdfResourcePolicy)
│       ├── excel/
│       │   ├── exporter.py       # ExcelExporter + ExcelOptions (mode, streaming, sheet_name, decimal_policy)
│       │   ├── workbook.py       # ExcelWorkbook + FormattedEngine + DataEngine
│       │   ├── worksheet.py      # FormattedSheet (دمج/طباعة) و DataSheet (إلحاق فقط، يعمل مع Streaming)
│       │   ├── styles.py         # Style → openpyxl مع cache، والألوان من tokens.css
│       │   ├── values.py         # الأنواع الأصلية، سياسة Decimal، تنسيقات الأرقام والتواريخ
│       │   └── renderers/        # Renderer لكل مكوّن في كل نمط
│       └── json.py
├── tests/                       # unittest: الجداول والصفحات
```

### الجداول

- قيمة الصف إما قيمة بسيطة يُنسّقها العمود، أو `TableCell(children=[...])` يعرض مكونات بتنسيقاتها الخاصة.
- `TableCell` يقبل `value` أو `children` وليس الاثنين، و`align=None` يرث محاذاة العمود.
- الصفوف قد تكون iterable كسول، ولا تُحوّل إلى قائمة؛ يتم التحقق من كل صف عند عرضه.
- ألوان الجداول وتباعد الخلايا متغيرات في `tokens.css` (`--rk-table-*`).

## طريقة إضافة مكوّن جديد

1. أضف Class مستقلًا تحت الحزمة المناسبة في `components/`.
2. صدّره من `__init__.py` المناسب وسجله في Registry.
3. أضف Renderer مستقلًا تحت `exporters/html/renderers/`.
4. أضف قالب Jinja2 وCSS عند الحاجة.
5. لا تضع HTML أو CSS أو حسابات داخل Component.
6. أضف اختبارًا أو مثالًا عامًا، ثم شغّل compile والأمثلة.

## تصدير PDF

`PdfExporter` في `exporters/pdf/` يولّد HTML كاملًا عبر `HtmlExporter` ثم يحوّله إلى PDF عبر WeasyPrint؛ لا توجد PDF Renderers للمكونات.

```python
from reportkit.exporters.pdf import PdfExporter

pdf_bytes = PdfExporter.export(document)            # bytes تبدأ بـ %PDF
with open("report.pdf", "wb") as file:              # الحفظ مسؤولية التطبيق
    file.write(pdf_bytes)
```

- WeasyPrint اعتماد اختياري: `pip install -e ".[pdf]"`، ويحتاج مكتبات Pango في النظام. عند غيابه يُرفع `ImportError` برسالة واضحة.
- الموارد: الصور المحلية تُضمَّن كـ data URI عبر `AssetResolver`. أثناء التحويل يُسمح فقط بـ `data:`، وبملفات داخل `base_url` إن مُرِّر؛ الشبكة وبقية الملفات المحلية تُمنع ويُرفع `PdfExportError` مع السبب الأصلي.
- Header/Footer المتكرر (`repeat=True`) يجب أن يأتي قبل المحتوى في الشجرة حتى يظهر من الصفحة الأولى (سلوك running elements في CSS).
- على Windows تُشغَّل اختبارات PDF عبر Docker:

```powershell
docker build -t reportkit-pdf .
docker run --rm reportkit-pdf
docker run --rm -v "${PWD}/examples:/app/examples" reportkit-pdf python -m examples.financial_movement.report --pdf
```

## تصدير Excel

```python
from reportkit.exporters.excel import ExcelExporter, ExcelOptions

xlsx = ExcelExporter().export(document, context)                                      # formatted: يشبه HTML/PDF
xlsx = ExcelExporter().export(document, context, ExcelOptions(mode="data", streaming=True))  # data: ورقة لكل جدول
```

- openpyxl اعتماد اختياري: `pip install -e ".[excel]"` (و Pillow للصور).
- لا حسابات ولا معادلات: القيم تُكتب كما وصلت، والنصوص تُخزن كنص دائمًا (حماية من Formula Injection).
- Decimal: يُكتب كرقم إذا كان ضمن 15 رقمًا معنويًا (دقة Excel)، وإلا يُرفع `ExcelExportError` أو يُكتب نصًا مع `decimal_policy="text"`.
- `formatted` لا يعمل مع `streaming=True` (يحتاج دمج خلايا وكتابة غير متسلسلة) ويحتفظ بالورقة كاملة في الذاكرة، ويستغرق نحو 2.5 ms لكل صف (50 ألف صف ≈ دقيقتان).
- للتقارير الضخمة (عشرات الآلاف من الصفوف فأكثر) استخدم `ExcelOptions(mode="data", streaming=True)`: ذاكرة شبه ثابتة (نحو 84 MB لـ 100 ألف صف).
- غير مدعوم: `Chart` و`PageCount` (وهما بلا Renderer في HTML أيضًا)، والصور البعيدة وصور SVG.

## تصدير Word

```python
from reportkit.exporters.word import WordExporter

docx_bytes = WordExporter().export(document, context)
```

- python-docx اعتماد اختياري: `pip install -e ".[word]"`. البناء مثل Excel: `word/document` (المستند والمحرك)، `word/renderers` (table/ و layout/)، `word/styles`، `word/values`.
- الشبكات (Grid/Row/InfoGrid) جداول بلا حدود، والصناديق المؤطرة جدول بخلية واحدة؛ RTL عبر `w:bidi` و`w:bidiVisual`.
- Header/Footer المتكرر يذهب إلى رأس/تذييل صفحة Word، و`PageNumber` يستخدم حقول PAGE و NUMPAGES.
- المنطق المشترك بين المصدّرين في `styles/tokens.py` و`styles/table.py` و`styles/borders.py` و`rendering/tracks.py` و`rendering/table.py`.

## التحقق

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t .
.\.venv\Scripts\python.exe -m examples.financial_movement.report
.\.venv\Scripts\python.exe -m compileall -q src examples tests
```

عند تعديل التخطيط، يجب فحص HTML الناتج بصريًا، خصوصًا: ترويسة الفندق، مركزية الشعار، RTL/LTR، عرض الجداول، عدم وجود تمرير أفقي، والطباعة على A4.
