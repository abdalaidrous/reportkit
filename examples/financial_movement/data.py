"""
Small, prepared data for the financial movement examples.

Everything here arrives ready for display, as it would from the calling application: amounts are already
formatted and the totals are already summed. ReportKit never calculates them.
"""

from reportkit.components.table import TableCell, TableColumn
from reportkit.components.typography import Text
from reportkit.styles.style import Style


def date_time(date, time):
    """
    A composite cell: the date with a smaller gray time underneath.
    """
    return TableCell(children=[
        Text(value=date, style=Style(font_size=10.5, color='#444444')),
        Text(value=time, style=Style(font_size=9, color='#777777', direction='ltr')),
    ])


def column(key, title, subtitle, width=None, nowrap=True, align='center'):
    """
    A centered bilingual column: Arabic title with an English subtitle.
    """
    return TableColumn(key=key, title=title, subtitle=subtitle, width=width, nowrap=nowrap, align=align, header_align=align)


BRANDING = {
    'name_en': 'Alahqaf Hotel', 'name_ar': 'فندق الاحقاف',
    'location_en': 'Saudi Arabia - Khobar', 'location_ar': 'السعودية (المملكة العربية) - الخبر',
    'address_en': '4034 11th St, Madinat Al Umal, Al Khobar 34442',
    'address_ar': '4034 الشارع الحادي عشر، مدينة العمال، الخبر 34442',
    'cr': '2552977145', 'vat': '2552977145',
}

# (English label, value, Arabic label), listed in RTL reading order: the first item sits on the right.
FILTERS = [('Date from', '13/11/2026', 'من تاريخ'), ('Date to', '14/11/2026', 'إلى تاريخ')]
METADATA = [('Printed by', 'عبدالله العيدروس', 'طبع بواسطة'), ('Printed at', '20/11/2026  01:02 PM', 'طبع في')]

MOVEMENT_COLUMNS = [
    column('voucher', 'رقم السند', 'Voucher No.'),
    column('date', 'التاريخ والوقت', 'Date & Time'),
    column('description', 'البيان', 'Description', nowrap=False),
    column('method', 'طريقة الدفع', 'Payment Method', nowrap=False),
    column('amount', 'المبلغ', 'Amount'),
    column('user', 'المستخدم', 'User'),
]

MOVEMENTS = [
    {'voucher': '000003', 'date': date_time('14/11/2026', '12:47 AM'), 'description': 'دفعة الحجز رقم 1', 'method': 'الدفع نقدًا', 'amount': '200.00 ﷼', 'user': 'عبدالله العيدروس'},
    {'voucher': '000002', 'date': date_time('13/11/2026', '11:55 PM'), 'description': 'دفعة الحجز رقم 1', 'method': 'الدفع نقدًا', 'amount': '100.00 ﷼', 'user': 'عبدالله العيدروس'},
    {'voucher': '000001', 'date': date_time('13/11/2026', '11:39 PM'), 'description': 'دفعة الحجز رقم 1', 'method': 'تمارا', 'amount': '100.00 ﷼', 'user': 'عبدالله العيدروس'},
]
MOVEMENTS_TOTAL = {'voucher': 'الإجمالي', 'amount': '400.00 ﷼'}

SUMMARY_COLUMNS = [
    column('method', 'طريقة الدفع', 'Method', width='40%', nowrap=False, align='right'),
    column('count', 'عدد الحركات', 'Count'),
    column('receipts', 'سندات القبض', 'Receipts'),
    column('net', 'الصافي', 'Net'),
]
SUMMARY_ROWS = [
    {'method': 'الدفع نقدًا', 'count': '2', 'receipts': '300.00', 'net': '300.00'},
    {'method': 'تمارا', 'count': '1', 'receipts': '100.00', 'net': '100.00'},
]
SUMMARY_TOTAL = {'method': 'الإجمالي (﷼)', 'count': '3', 'receipts': '400.00', 'net': '400.00'}
