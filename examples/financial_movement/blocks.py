"""
Bilingual building blocks of the financial movement report, composed from plain ReportKit components.

Each function returns a component that the examples pass to ReportBuilder.header(), .add() or .footer().
"""

from pathlib import Path

from reportkit.components.layout import Box, Column, Grid, Row
from reportkit.components.media import Image
from reportkit.components.typography import Heading, Text
from reportkit.styles.style import Style

from .styles import BORDER, BRAND_NAME, FRAME, LABEL, ROW_BORDER, SECONDARY, VALUE

LOGO = Path(__file__).with_name('logo.png')


def hotel_identity(branding):
    """
    Framed hotel box: Arabic name on the right, logo centered, English name on the left, and the VAT/C.R strip.
    """
    return Box(style=FRAME.merge(Style(margin_bottom=14)), children=[
        Grid(columns='1fr auto 1fr', style=Style(direction='rtl', gap=16, padding='14px 16px', align_items='center'), children=[
            brand_column(branding, 'ar', 'rtl', 'right'),
            Image(src=LOGO.as_uri(), alt='Hotel logo', width='76', height='76'),
            brand_column(branding, 'en', 'ltr', 'left'),
        ]),
        Grid(columns='1fr 1fr', style=Style(direction='rtl', gap=0, background_color='#f5f5f5', border_top=BORDER), children=[
            labeled_value('الرقم الضريبي', branding['vat'], 'VAT No', divider=True),
            labeled_value('السجل التجاري', branding['cr'], 'C.R'),
        ]),
    ])


def brand_line(branding):
    """
    One-line hotel name in both languages; small enough for a repeated page header, which is sized to its content.
    """
    return Text(value=f"{branding['name_ar']} — {branding['name_en']}", style=BRAND_NAME.merge(Style(font_size=11, direction='rtl')))


def brand_column(branding, language, direction, text_align):
    """
    Hotel name, location and address in one language.
    """
    align = Style(text_align=text_align)
    return Column(direction=direction, align='start', gap='2px', children=[
        Heading(value=branding[f'name_{language}'], level=2, style=BRAND_NAME.merge(align)),
        Text(value=branding[f'location_{language}'], style=SECONDARY.merge(align)),
        Text(value=branding[f'address_{language}'], style=SECONDARY.merge(align)),
    ])


def labeled_value(arabic, value, english, divider=False, style=None):
    """
    One bilingual cell laid out as: Arabic label | value | English label.

    ``divider`` draws the separator on the cell's left edge, so set it on the first (right-hand) cell of an RTL grid.
    """
    cell = Style(direction='rtl', padding='8px 12px', border_left=BORDER if divider else None)
    return Row(justify='space-between', align='center', gap='8px', style=cell.merge(style) if style else cell, children=[
        Text(value=arabic, style=LABEL), Text(value=value, style=VALUE), Text(value=english, style=LABEL),
    ])


def report_title(english, arabic):
    """
    Arabic title on the right, English subtitle on the left, heavy rule underneath.
    """
    return Grid(columns='1fr 1fr', style=Style(direction='rtl', gap=16, align_items='center', padding='4px 0 10px', border_bottom='2px solid #222222'), children=[
        Heading(value=arabic, level=2, style=Style(font_size=20, font_weight=700, text_align='right', margin=0)),
        Text(value=english, style=Style(font_size=11, color='#555555', letter_spacing=0.5, text_align='left', margin=0)),
    ])


def section_title(english, arabic):
    """
    Bold Arabic section title on the right, small English title on the left.
    """
    return Grid(columns='1fr 1fr', style=Style(direction='rtl', gap=16, align_items='end', margin_bottom=6), children=[
        Heading(value=arabic, level=3, style=Style(font_size=14, font_weight=700, text_align='right', margin=0)),
        Text(value=english, style=Style(font_size=10, color='#555555', text_align='left', margin=0)),
    ])


def labeled_grid(items, framed=False):
    """
    Two-column RTL grid of bilingual cells; items are (english, value, arabic) and an odd count leaves an empty cell.
    """
    cells = list(items) + ([None] if len(items) % 2 else [])
    last_row = (len(cells) - 1) // 2
    children = []
    for index, item in enumerate(cells):
        divider = index % 2 == 0
        cell = Style(border_bottom=ROW_BORDER if index // 2 < last_row else None)
        if item is None:
            children.append(Box(style=cell.merge(Style(border_left=BORDER if divider else None))))
        else:
            english, value, arabic = item
            children.append(labeled_value(arabic, value, english, divider=divider, style=cell.merge(Style(padding='10px 14px'))))
    frame = FRAME if framed else Style()
    return Grid(columns='1fr 1fr', style=frame.merge(Style(direction='rtl', gap=0, margin_bottom=14)), children=children)
