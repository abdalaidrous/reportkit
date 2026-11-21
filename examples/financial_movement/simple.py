"""
Example 1 — the smallest useful report: a title, one table with its prepared total, and page numbers.

Run from the project root:

    python -m examples.financial_movement.simple

Writes examples/financial_movement/output/simple.html.
"""

from pathlib import Path

from reportkit.builders import ReportBuilder
from reportkit.components.typography import Heading
from reportkit.rendering.context import RenderingContext

from .data import MOVEMENT_COLUMNS, MOVEMENTS, MOVEMENTS_TOTAL

OUTPUT = Path(__file__).with_name('output')
CONTEXT = RenderingContext(language='ar', direction='rtl')


def report_builder():
    """
    Title, movements table with its total row, and the page number.
    """
    return (
        ReportBuilder('Financial Movement Report')
        .add(Heading(value='تقرير الحركة المالية', level=2))
        .table(MOVEMENT_COLUMNS, MOVEMENTS, totals=MOVEMENTS_TOTAL)
        .page_number('صفحة {page} من {pages}')
    )


def main():
    """
    Export the report to HTML.
    """
    OUTPUT.mkdir(exist_ok=True)
    return report_builder().export_to('html', OUTPUT / 'simple.html', CONTEXT)


if __name__ == '__main__':
    print(main())
