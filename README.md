# ReportKit

Build reports from reusable components and export the same report to **HTML**, **PDF**, **Excel (XLSX)** and **Word (DOCX)**.
ReportKit is built for bilingual Arabic/English documents: right-to-left and left-to-right text, mixed-direction values
and RTL tables are handled in every format.

ReportKit is a presentation library. Your application prepares the rows, totals and summaries; ReportKit only lays them
out, styles them and exports them. It never computes or aggregates report data.

## Installation

```bash
pip install pyreportkit           # HTML export
pip install "pyreportkit[pdf]"    # + PDF (WeasyPrint)
pip install "pyreportkit[excel]"  # + Excel (openpyxl, Pillow)
pip install "pyreportkit[word]"   # + Word (python-docx)
pip install "pyreportkit[all]"    # every exporter
```

PDF export uses [WeasyPrint](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html), which needs the Pango
system libraries (`apt install libpango-1.0-0 libpangoft2-1.0-0` on Debian/Ubuntu). On Windows, the simplest option is
the provided `Dockerfile`.

Requires Python 3.10 or newer.

## Quick start: ReportBuilder

`ReportBuilder` is the recommended way to build a report. Chain the parts top to bottom, then `build()` the `Report` or
export it directly:

```python
from reportkit.builders import ReportBuilder
from reportkit.components.table import TableColumn
from reportkit.components.typography import Heading
from reportkit.rendering.context import RenderingContext

columns = [
    TableColumn(key="voucher", title="رقم السند", subtitle="Voucher No."),
    TableColumn(key="method", title="طريقة الدفع", subtitle="Payment Method"),
    TableColumn(key="amount", title="المبلغ", subtitle="Amount", format="currency", currency="﷼"),
]
rows = [
    {"voucher": "000002", "method": "الدفع نقدًا", "amount": 300},
    {"voucher": "000001", "method": "تمارا", "amount": 100},
]

builder = (
    ReportBuilder("Financial Movement Report")
    .page(size="A4", margin="10mm 11mm 12mm", page_number_position="bottom-center")
    .header(Heading(value="فندق الاحقاف", level=2))
    .add(Heading(value="تقرير الحركة المالية", level=3))
    .table(columns, rows, totals={"voucher": "الإجمالي", "amount": 400})
    .footer(Heading(value="طبع بواسطة: عبدالله", level=4))
    .page_number("Page {page} of {pages}")
)

context = RenderingContext(language="ar", direction="rtl")
builder.export_to("html", "report.html", context)       # "pdf", "xlsx"/"excel", "docx"/"word"
pdf_bytes = builder.export("pdf", context)               # or get the bytes
report = builder.build()                                 # or the Report, for any exporter
```

| Method | What it does |
|---|---|
| `ReportBuilder(title)` | Starts a report. |
| `.page(size=, orientation=, margin=, page_number_position=, ...)` | Page settings; `margin` is a CSS shorthand of 1 to 4 values. |
| `.header(*components, repeat=False)` | The header. `repeat=True` prints it on every page. |
| `.add(*components)` | Any components, in order. |
| `.table(columns, rows, totals=, title=, style=, table_style=)` | A table of prepared rows (mappings or `TableRow`) and an optional prepared totals row. |
| `.spacer(height)` / `.page_break()` | Vertical space / a forced page break. |
| `.footer(*components, repeat=False)` | The footer. `repeat=True` prints it on every page. |
| `.page_number(format)` | Page numbers in print and PDF, at `page_number_position`. |
| `.build()` | Returns the `Report`. |
| `.export(format, context, **options)` | Returns the exported bytes. |
| `.export_to(format, target, context, **options)` | Writes to a path or a binary stream. |

Things the builder takes care of:

- **Order.** The header always comes first, a repeated footer before the content (so it shows from the first page), and
  a normal footer and the page number at the end, whatever order you call the methods in.
- **No calculations.** `totals` is passed prepared and becomes the table's total row.
- **Lazy rows.** Rows can be a generator or a database cursor; they are read one at a time while exporting. A generator
  can only be read once, so build the report again for each export.
- **Exporter options** pass through as keywords: `export("pdf", context, options=PdfOptions(workers=4))`,
  `export("xlsx", context, options=ExcelOptions(mode="data", streaming=True))`.

For finer control over a table, `TableBuilder` defines it column by column:

```python
from reportkit.builders import TableBuilder

table = (
    TableBuilder()
    .column("voucher", "رقم السند", subtitle="Voucher No.", align="center")
    .column("amount", "المبلغ", subtitle="Amount", format="currency", currency="﷼")
    .rows(rows)
    .totals({"voucher": "الإجمالي", "amount": 400})
    .table_style(bordered=False, ruled=True)
    .build()
)
builder.add(table)
```

Three complete, runnable examples (simple, branded, every format) are in [`examples/`](examples/README.md).

## Building from components

The builder is a thin layer over plain components, and you can always build the tree yourself; `build()` returns
exactly this kind of `Report`.

```python
from reportkit.components.document import Page, Report
from reportkit.components.layout import Grid
from reportkit.components.table import Table, TableCell, TableColumn, TableRow
from reportkit.components.typography import Heading, Text
from reportkit.rendering.context import RenderingContext
from reportkit.styles.style import Style

report = Report(title="Financial Movement Report", children=[
    Page(size="A4", orientation="portrait", page_number_position="bottom-center", children=[
        Grid(columns="1fr 1fr", children=[
            Heading(value="تقرير الحركة المالية", level=2, style=Style(text_align="right")),
            Text(value="Financial Movement Report", style=Style(text_align="left")),
        ]),
        Table(
            columns=[
                TableColumn(key="voucher", title="رقم السند", subtitle="Voucher No."),
                TableColumn(key="date", title="التاريخ", subtitle="Date"),
                TableColumn(key="amount", title="المبلغ", subtitle="Amount", format="number"),
            ],
            rows=[
                TableRow(values={
                    "voucher": "000004",
                    "date": TableCell(children=[Text(value="14/11/2026"), Text(value="12:47 AM", style=Style(font_size=9, color="#777777"))]),
                    "amount": 200,
                }),
            ],
            footer=TableRow(values={"voucher": "الإجمالي", "amount": 200}, kind="total"),
        ),
    ]),
])

context = RenderingContext(language="ar", direction="rtl")
```

Rows can be any iterable, including generators and database cursors: they are read one at a time and never loaded into
a list.

## Exporting

Every exporter returns `bytes`; saving or sending them is up to your application.

### HTML

```python
import reportkit.exporters.html
from reportkit.exporters.html.exporter import HtmlExporter

html = HtmlExporter().export(report, context)
```

### PDF

```python
from reportkit.exporters.pdf import PdfExporter

pdf = PdfExporter.export(report, context)
```

The PDF is rendered from the same HTML and CSS. Only embedded images (`data:` URIs) and files inside an optional
`base_url` folder are loaded; network resources are refused, and any resource that cannot be loaded fails the export
instead of producing an incomplete PDF.

Large reports (tens of thousands of rows) are laid out in chunks of about `chunk_rows` table rows and merged with
pypdf, so memory stays bounded by one chunk instead of growing with the report. Rows may be a lazy iterator (for
example a database cursor); they are read as the chunks need them and never all kept in memory. Totals and other
aggregates must be passed already computed (for example as the table `footer`). `export_to` writes to a file path or a
binary stream:

```python
from reportkit.exporters.pdf import PdfExporter, PdfOptions

PdfExporter.export_to(report, "report.pdf", context)                                    # default: 500-row chunks
PdfExporter.export_to(report, stream, context, options=PdfOptions(chunk_rows=None))     # one pass, as before
```

Each chunk ends at a real page break, so pages break where a single-pass layout breaks them. Only tables placed directly
in a `Page` (or the `Report`) are split; the column widths of a split table are measured on its first chunk and kept
for the rest, and page numbers are stamped after merging. Layout time is still about the same per row (WeasyPrint);
what chunking removes is the memory growth.

`PdfOptions(workers=8)` lays chunks out in parallel processes (10,000 rows: about 3 minutes instead of 13). Each chunk
then ends on its own last page, so a page at each chunk boundary is only partly filled, and each worker needs about as
much memory as one chunk (about 0.5 GB for 500 rows). On Windows and macOS the calling script must be guarded with
`if __name__ == "__main__":`, as for any `multiprocessing` code.

### Excel

```python
from reportkit.exporters.excel import ExcelExporter, ExcelOptions

xlsx = ExcelExporter().export(report, context)                                              # looks like the PDF
xlsx = ExcelExporter().export(report, context, ExcelOptions(mode="data", streaming=True))   # one typed sheet per table
```

- `formatted` (default): one printable sheet with merged cells, colors, borders, logo, RTL and print settings.
- `data`: analysis-ready sheets with real numbers and dates, frozen headers and AutoFilter. With `streaming=True` memory
  stays flat, which is the right choice for very large reports.
- Values are written as they arrive: no formulas, text is always stored as text (formula injection safe), and decimals
  beyond Excel's 15 significant digits raise an error unless `decimal_policy="text"`.

### Word

```python
from reportkit.exporters.word import WordExporter

docx = WordExporter().export(report, context)
WordExporter().export_to(report, "report.docx", context)   # or a binary stream
```

Tables repeat their header row on every page, repeating headers and footers go to the Word page header and footer, and
page numbers use Word's PAGE and NUMPAGES fields.

Large tables keep memory flat: rows may be a lazy iterator, and finished rows of tables placed in the document body are
moved to temporary storage (memory, then disk) and streamed back into the file on save. 10,000 rows take about 43 s and
70 MB; the output is identical to building the whole document in memory.

### Exporter registry

```python
import reportkit.exporters.html, reportkit.exporters.pdf, reportkit.exporters.excel, reportkit.exporters.word
from reportkit.exporters.registry import ExporterRegistry

exporter = ExporterRegistry.get("xlsx")()   # "html", "pdf", "excel"/"xlsx", "word"/"docx"
```

## Components

| Group | Components |
|---|---|
| Document | `Report`, `Page`, `Header`, `Footer` |
| Layout | `Box`, `Section`, `Row`, `Column`, `Grid`, `Spacer`, `Divider` |
| Typography | `Text`, `Heading`, `RichText`, `TextSpan` |
| Tables | `Table`, `TableColumn`, `TableRow`, `TableCell`, `TableStyle` |
| Information | `KeyValue`, `InfoGrid` |
| Media | `Image` |
| Pagination | `PageBreak`, `PageNumber` |

Styles are immutable `Style` objects; table colors and spacing come from CSS design tokens shared by every exporter.

## Development

```bash
pip install -r requirements-dev.txt
python -m pytest tests
docker build -t reportkit . && docker run --rm reportkit   # full suite, including PDF
```
