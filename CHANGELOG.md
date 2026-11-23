# Changelog

All notable changes to pyreportkit. The format follows [Keep a Changelog](https://keepachangelog.com/), and versions
follow [Semantic Versioning](https://semver.org/).

## [0.2.1] - 2026-11-23

### Added

- `TableStyle(header_style=Style(...))`: a style merged over the table's header cells in HTML, PDF, Excel and Word
  (for example a brand background with white text); a styled header's subtitles follow its text color.

### Fixed

- A compact table sets its smaller font size on the table instead of on each cell, so a `Style(font_size=...)` given
  to the table now applies to its cells.

## [0.2.0] - 2026-11-22

### Added

- **Builder API** (`reportkit.builders`): `ReportBuilder` builds a one-page `Report` with ordered header, content,
  repeated footer and page number; `.table(columns, rows, totals=)`, `.chart()`, `.qr_code()`, `.page_count()`,
  `.export(format)` and `.export_to(format, target)`. `TableBuilder` defines columns one by one and turns prepared
  mappings into rows lazily. `ReportExport` exports by format name (`html`, `pdf`, `xlsx`/`excel`, `docx`/`word`).
- **`QRCode`** component (`reportkit.components.media`): encodes a prepared value; a sharp SVG in HTML and PDF, a PNG in
  Excel and Word, always on a white background. Options: `size`, `error_correction` (L, M, Q, H), `quiet_zone`, `alt`.
- **`Chart`** and **`ChartSeries`**: bar, line and pie charts of prepared values. HTML and PDF draw SVG shapes with
  HTML labels (Arabic is shaped correctly); Excel gets a native, editable chart; Word gets the table of values.
  Options: `title`, `width`, `height`, `decimals`, `legend`, `show_values`, per-series `color`. New design tokens
  `--rk-chart-*`.
- **`PageCount`** rendering: the total number of printed pages (`"Total pages: {pages}"`) in the content or in a
  repeating header or footer, in PDF (including chunked and parallel exports, where the merged total is stamped
  afterwards), Word (NUMPAGES field) and Excel (printed footer).
- **Large PDF reports**: `PdfOptions(chunk_rows=500)` lays long tables out in chunks merged with pypdf, so memory stays
  bounded; `PdfOptions(workers=N)` lays chunks out in parallel processes.
- **`export_to(document, target)`** for PDF, Excel and Word: writes to a path or a binary stream without keeping a
  second copy in memory (Excel goes through a temporary file).
- Validators for media and pagination components (`reportkit.validators.media`, `reportkit.validators.pagination`).

### Changed

- **segno** is now a required dependency (QR codes); `pypdf` joins the `pdf` extra.
- Word export of large tables keeps memory flat: finished rows are spooled to disk and streamed into the file
  (10,000 rows: about 43 s and 70 MB instead of 179 s and 872 MB).
- `PageNumber` and `Image` validation moved from the components to `reportkit.validators`.

## [0.1.0] - 2026-11-21

### Added

- First release: components (document, layout, typography, tables, information, media, pagination), styles and design
  tokens, and the HTML, PDF (WeasyPrint), Excel (openpyxl) and Word (python-docx) exporters, with RTL/LTR support.

[0.2.1]: https://github.com/abdalaidrous/reportkit/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/abdalaidrous/reportkit/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/abdalaidrous/reportkit/releases/tag/v0.1.0
