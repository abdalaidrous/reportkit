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

## Quick start

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

### Builder

`ReportBuilder` builds the same tree fluently. It returns a plain `Report`, so every exporter works unchanged, and it
places a repeated header or footer before the content so it shows from the first page.

```python
from reportkit.builders import ReportBuilder, TableBuilder

report = (
    ReportBuilder("Financial Movement Report")
    .page(size="A4", margin="10mm 11mm 12mm", page_number_position="bottom-center")
    .header(Heading(value="تقرير الحركة المالية", level=2))
    .table(columns, rows, totals={"voucher": "الإجمالي", "amount": 200})   # rows: mappings or TableRow, kept lazy
    .spacer(20)
    .footer(Text(value="Printed by ReportKit"), repeat=True)
    .page_number("Page {page} of {pages}")
    .build()
)

pdf_bytes = ReportBuilder("Quick").table(columns, rows).export("pdf", context)
ReportBuilder("Quick").table(columns, rows).export_to("docx", "report.docx", context)

table = TableBuilder().column("voucher", "رقم السند", subtitle="Voucher No.").rows(rows).totals(total).build()
```

Totals are passed prepared; the builder never calculates. Exporter options go through as keywords, for example
`export("pdf", context, options=PdfOptions(workers=4))`.

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
