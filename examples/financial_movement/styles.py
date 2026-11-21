"""
Visual tokens shared by the financial movement examples.
"""

from reportkit.components.table import TableStyle
from reportkit.styles.style import Style

BORDER = '1px solid #dedede'
ROW_BORDER = '1px solid #e5e5e5'
FRAME = Style(border_width=1, border_style='solid', border_color='#dedede', border_radius=6, overflow='hidden')

BRAND_NAME = Style(font_size=15, font_weight=700, margin=0)
SECONDARY = Style(font_size=9, color='#777777', margin=0)
LABEL = Style(font_size=9, color='#777777', margin=0)
VALUE = Style(font_size=11, font_weight=700, margin=0, direction='ltr')

TABLE = Style(font_size=10.5)
MOVEMENTS_TABLE = TableStyle(bordered=False, layout='auto')
SUMMARY_TABLE = TableStyle(bordered=False, ruled=True, layout='auto')
