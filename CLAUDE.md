# ReportKit — دليل المشروع لـ Claude

## الهدف

ReportKit مكتبة Python مستقلة لبناء التقارير من مكونات قابلة لإعادة الاستخدام، ثم تحويلها إلى HTML أو صيغ تصدير أخرى. المكتبة مسؤولة عن بنية التقرير، التنسيق، العرض، الأصول، والطباعة؛ أما البيانات والحسابات والإجماليات فتأتي جاهزة من التطبيق المستدعي.

المشروع لا يعتمد على Django، ولا يجب أن يضيف منطقًا خاصًا بتقرير مالي واحد إلى المكونات العامة.

## مثال التشغيل الحالي

المثال الرئيسي هو تقرير الحركة المالية:

```powershell
pip install -e .
python -m examples.financial_movement.simple     # 1: عنوان + جدول بإجمالي + أرقام الصفحات
python -m examples.financial_movement.branded    # 2: التصميم الكامل (reference_preview.html)، و --pdf
python -m examples.financial_movement.formats    # 3: TableBuilder وصفوف generator وترويسة متكررة وكل الصيغ
```

المخرجات في `examples/financial_movement/output/`، والشرح في `examples/README.md`. الأمثلة الثلاثة مبنية بـ `ReportBuilder` وببيانات صغيرة، وتشترك في `data.py` و`styles.py` و`blocks.py` (مكونات ثنائية اللغة: `hotel_identity`, `brand_line`, `report_title`, `section_title`, `labeled_grid`). يتم تمرير الصفوف والإجماليات جاهزة، ولا تحسب ReportKit أي إجماليات أو مجاميع.

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
│   ├── README.md                # شرح الأمثلة الثلاثة
│   └── financial_movement/
│       ├── data.py              # بيانات صغيرة جاهزة
│       ├── styles.py            # Styles الخاصة بالأمثلة
│       ├── blocks.py            # مكونات ثنائية اللغة مركبة
│       ├── simple.py            # مثال 1
│       ├── branded.py           # مثال 2 (يستخدمه اختبارات المصدّرين)
│       ├── formats.py           # مثال 3
│       ├── logo.png
│       ├── reference_preview.html  # التصميم المستهدف لـ branded.py
│       └── output/              # المخرجات المولدة
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
│   ├── builders/                # واجهة Builder: report.py (ReportBuilder)، table.py (TableBuilder)، export.py (ReportExport)
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
│       │   ├── exporter.py       # PdfExporter: export (bytes) و export_to (مسار/stream)؛ مسار واحد أو أجزاء
│       │   ├── options.py        # PdfOptions(chunk_rows=500 أو None)
│       │   ├── chunking/         # flow (صفوف كسولة) → planner (الجزء التالي) → html → layout (قراءة صناديق WeasyPrint) → renderer
│       │   ├── assembly/         # merger.py (pypdf) و numbering.py (طبقة أرقام الصفحات بعد الدمج)
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

## Builder

```python
from reportkit.builders import ReportBuilder, TableBuilder

report = ReportBuilder("Title").page(margin="10mm 11mm").header(...).table(columns, rows, totals=total).footer(...).page_number().build()
ReportBuilder("Title").table(columns, rows).export_to("pdf", "report.pdf", context, options=PdfOptions(workers=4))
```

- طبقة فوق المكونات فقط: `build()` يُرجع `Report` عاديًا بصفحة واحدة، والبناء المباشر بالمكونات يبقى كما هو. التحقق يبقى في المكونات والـ Validators.
- الترتيب يُدار داخليًا: الترويسة أولًا، والتذييل المتكرر قبل المحتوى، والتذييل غير المتكرر ثم رقم الصفحة في النهاية، مهما كان ترتيب الاستدعاء.
- `TableBuilder` يغلّف الصفوف في `PreparedRows`: تحويل كسول من dict إلى `TableRow` يعيد قراءة المصدر في كل تكرار. `totals` يصبح `TableRow(kind="total")` ولا يُحسب شيء.
- `ReportExport` يستورد حزمة المصدّر حسب الصيغة (`html`, `pdf`, `excel`/`xlsx`, `word`/`docx`) ثم يستخدم `ExporterRegistry`، ويفضّل `export_to` للمصدّر إن وُجد. الخيارات تمر كـ kwargs.
- الاختبار `tests/test_builders.py` يقارن HTML مثال الحركة المالية المبني بالـ Builder مع البناء المباشر.

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
- التقارير الضخمة: `PdfOptions(chunk_rows=500)` افتراضيًا. الجداول المباشرة داخل `Page` (أو `Report`) تُقسَّم إلى أجزاء؛ كل جزء تقرير صغير يُخطط بـ WeasyPrint وتُحذف صفحته الأخيرة غير المكتملة وتُعاد صفوفها مع الجزء التالي، فتنكسر الصفحات كما في المسار الواحد. عرض الأعمدة يُقاس من الجزء الأول ويُثبت (`TableFragment` + `width` بالـ px)، و`rk-pdf-fragment--continued` في `pdf.css` يحاكي استئناف الجدول في صفحة جديدة. الترقيم يُختم بعد الدمج بطبقة شفافة (`string-set`). التقرير الذي يتسع في جزء واحد يُخطط مرة واحدة كما كان.
- pypdf ضمن `[pdf]`؛ بدونه يُطلق تحذير ويُستخدم المسار الواحد. الصفوف تُقرأ كسولًا ولا تُحمّل كلها، والإجماليات تأتي جاهزة من التطبيق.
- `export_to(document, target)` يكتب إلى مسار أو stream ثنائي.
- `PdfOptions(workers=N)` (افتراضيًا 1): `ParallelPdfRenderer` يخطط الجزء الأول محليًا لقياس عرض الأعمدة، ثم يرسل HTML الأجزاء الباقية إلى `ProcessPoolExecutor` ويجمعها بالترتيب. كل جزء يحتفظ بصفحته الأخيرة، فتظهر صفحة غير ممتلئة عند كل حد، و`rk-pdf-fragment--continues` يجعل نهاية الجدول كجدول مقسوم. 10 آلاف صف: 181 ث بـ 8 عمليات مقابل 766 ث تسلسليًا.
- الموارد: الصور المحلية تُضمَّن كـ data URI عبر `AssetResolver`. أثناء التحويل يُسمح فقط بـ `data:`، وبملفات داخل `base_url` إن مُرِّر؛ الشبكة وبقية الملفات المحلية تُمنع ويُرفع `PdfExportError` مع السبب الأصلي.
- Header/Footer المتكرر (`repeat=True`) يجب أن يأتي قبل المحتوى في الشجرة حتى يظهر من الصفحة الأولى (سلوك running elements في CSS).
- على Windows تُشغَّل اختبارات PDF عبر Docker:

```powershell
docker build -t reportkit-pdf .
docker run --rm reportkit-pdf
docker run --rm -v "${PWD}/examples:/app/examples" reportkit-pdf python -m examples.financial_movement.branded --pdf
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
WordExporter().export_to(document, "report.docx", context)   # مسار أو stream ثنائي
```

- python-docx اعتماد اختياري: `pip install -e ".[word]"`. البناء مثل Excel: `word/document` (المستند والمحرك)، `word/renderers` (table/ و layout/)، `word/styles`، `word/values`.
- الشبكات (Grid/Row/InfoGrid) جداول بلا حدود، والصناديق المؤطرة جدول بخلية واحدة؛ RTL عبر `w:bidi` و`w:bidiVisual`.
- Header/Footer المتكرر يذهب إلى رأس/تذييل صفحة Word، و`PageNumber` يستخدم حقول PAGE و NUMPAGES.
- الجداول الضخمة: `renderers/table/rows.py` (`TableRows`) يضيف الصفوف دون `add_row`/`len(table.rows)`/`table.cell` في python-docx (كلها تمر على الجدول كاملًا)، وينقل الصفوف المنتهية لجداول جسم المستند إلى `document/spool.py` (`RowSpool`) كل 200 صف مع تعليق علامة في مكانها؛ `document/package.py` يعيد كتابة الحزمة ويضخ الصفوف مكان العلامة عند الحفظ. الصفوف التي يصلها rowspan تبقى في الشجرة.
- `styles/text.py` يبني خصائص الفقرة والـ run مرة لكل (نمط، اتجاه) وينسخها (`lru_cache` + `deepcopy`)؛ الناتج مطابق بايتًا ببايت. 10 آلاف صف: 43 ث و70MB (كان 179 ث و872MB).
- المنطق المشترك بين المصدّرين في `styles/tokens.py` و`styles/table.py` و`styles/borders.py` و`rendering/tracks.py` و`rendering/table.py`.

## التحقق

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t .
.\.venv\Scripts\python.exe -m examples.financial_movement.branded
.\.venv\Scripts\python.exe -m compileall -q src examples tests
```

عند تعديل التخطيط، يجب فحص HTML الناتج بصريًا، خصوصًا: ترويسة الفندق، مركزية الشعار، RTL/LTR، عرض الجداول، عدم وجود تمرير أفقي، والطباعة على A4.
