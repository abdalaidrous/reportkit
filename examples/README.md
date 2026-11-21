# ReportKit examples

Three runnable examples of the same hotel **financial movement report**, built with `ReportBuilder` and a small data
set. Each one adds a step over the previous one, so read them in order.

| # | File | Shows | Output |
|---|---|---|---|
| 1 | [`simple.py`](financial_movement/simple.py) | The smallest report: a title, one table with its total, page numbers. | `simple.html` |
| 2 | [`branded.py`](financial_movement/branded.py) | The full design: hotel header with logo, filters, two tables, footer, A4 page settings. | `branded.html`, `branded.pdf` |
| 3 | [`formats.py`](financial_movement/formats.py) | `TableBuilder`, native values (Decimal, datetime), rows from a generator, repeated header/footer, every export format. | `formats.html/.pdf/.xlsx/.docx`, `formats_data.xlsx` |

## Run

From the project root, after `pip install -e ".[excel,word]"`:

```powershell
python -m examples.financial_movement.simple
python -m examples.financial_movement.branded
python -m examples.financial_movement.formats
```

Files are written to `examples/financial_movement/output/`. PDF needs WeasyPrint and its Pango libraries; on Windows
use Docker:

```powershell
docker build -t reportkit-pdf .
docker run --rm -v "${PWD}/examples:/app/examples" reportkit-pdf sh -c "python -m examples.financial_movement.branded --pdf && python -m examples.financial_movement.formats"
```

Page numbers are print margin boxes: they appear in the PDF and in the browser print preview (Ctrl+P), not on screen.

## Files

```text
financial_movement/
├── data.py        # prepared data: rows, totals, branding, filters (no calculations anywhere)
├── styles.py      # Style and TableStyle tokens shared by the examples
├── blocks.py      # bilingual building blocks: hotel_identity, brand_line, report_title, section_title, labeled_grid
├── simple.py      # example 1
├── branded.py     # example 2
├── formats.py     # example 3
├── logo.png
├── reference_preview.html   # the target design of branded.py (hand-written, not generated)
└── output/        # generated files
```

## 1. Simple report

```python
ReportBuilder('Financial Movement Report')
    .add(Heading(value='تقرير الحركة المالية', level=2))
    .table(MOVEMENT_COLUMNS, MOVEMENTS, totals=MOVEMENTS_TOTAL)
    .page_number('صفحة {page} من {pages}')
    .export_to('html', 'simple.html', RenderingContext(language='ar', direction='rtl'))
```

- `MOVEMENT_COLUMNS` is a list of `TableColumn`; `MOVEMENTS` a list of plain dicts keyed by column. The builder turns
  each dict into a `TableRow` as it is read.
- `totals` is already summed by the application and becomes the table's total row.
- A cell can hold components instead of a value: `date_time()` in `data.py` returns a `TableCell` with the date and a
  smaller gray time underneath.

## 2. Branded report

```python
ReportBuilder('Financial Movement Report')
    .page(size='A4', orientation='portrait', margin='10mm 11mm 12mm', page_number_position='bottom-center')
    .header(hotel_identity(BRANDING))
    .add(report_title('Financial Movement Report', 'تقرير الحركة المالية'))
    .add(labeled_grid(FILTERS))
    .table(MOVEMENT_COLUMNS, MOVEMENTS, style=TABLE, table_style=MOVEMENTS_TABLE)
    .spacer(20)
    .add(section_title('Summary by Payment Method', 'الملخص حسب طريقة الدفع'))
    .table(SUMMARY_COLUMNS, SUMMARY_ROWS, totals=SUMMARY_TOTAL, style=TABLE, table_style=SUMMARY_TABLE)
    .spacer(20)
    .footer(labeled_grid(METADATA, framed=True))
    .page_number('Page {page} of {pages}')
```

- The blocks in `blocks.py` are ordinary functions returning components (`Grid`, `Box`, `Row`, `Image`...). Write your
  own the same way and pass them to `.header()`, `.add()` or `.footer()`.
- `margin` is a CSS shorthand: `'10mm 11mm 12mm'` means top 10, left and right 11, bottom 12.
- `style` sets the table font; `table_style` sets borders, rules and column sizing (`layout='auto'` sizes by content).

## 3. Every format

```python
table = (
    TableBuilder()
    .column('date', 'التاريخ والوقت', subtitle='Date & Time', format='datetime', date_format='%d/%m/%Y %I:%M %p')
    .column('amount', 'المبلغ', subtitle='Amount', format='currency', currency='﷼')
    ...
    .rows(fetch_movements())          # a generator, like a database cursor
    .totals(TOTAL)
    .build()
)

builder = (
    ReportBuilder('Financial Movement Report')
    .page(margin='20mm 11mm 16mm', page_number_position='bottom-right')
    .header(brand_line(BRANDING), repeat=True)
    .footer(Text(value='تقرير آلي — ReportKit'), repeat=True)
    .add(table)
)
builder.export_to('xlsx', 'formats_data.xlsx', context, options=ExcelOptions(mode='data', streaming=True))
```

- Values stay native (`Decimal`, `datetime`): the column formats them for HTML, PDF and Word, while Excel stores real
  numbers and dates.
- Rows are read lazily. A generator can be read only once, so `main()` builds the report again for each format.
- `repeat=True` prints the header and footer on every page, inside the page margins: keep them short (`brand_line`)
  and the top and bottom margins tall enough for them. The page number moves to `bottom-right` because the repeated
  footer takes the bottom center.
- The builder places repeated sections before the content, which print CSS requires; so on screen (not in the PDF)
  the footer shows under the header.
- Exporter options pass through: `options=ExcelOptions(...)`, `options=PdfOptions(workers=4)`.
