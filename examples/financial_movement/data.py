"""
Prepared display data transcribed from the supplied financial movement PDF.
"""

from reportkit.components.table import TableCell
from reportkit.components.typography import Text
from reportkit.styles.style import Style


def date_time(date, time):
    """
    A custom cell: the date with a smaller gray time underneath (children keep their own styles).
    """
    return TableCell(children=[
        Text(value=date, style=Style(font_size=10.5, color='#444444')),
        Text(value=time, style=Style(font_size=9, color='#777777', direction='ltr')),
    ])


BRANDING = {
    'name_en': 'Alahqaf Hotel', 'name_ar': 'فندق الاحقاف',
    'location_en': 'Saudi Arabia - Khobar', 'location_ar': 'السعودية (المملكة العربية) - الخبر',
    'address_en': 'EKJA4034, 4034 11th St, 6997, Madinat Al Umal, Al Khobar 34442, Saudi Arabia',
    'address_ar': 'EKJA4034، 4034 الشارع الحادي عشر، 6997، مدينة العمال، الخبر 34442، السعودية',
    'cr': '2552977145', 'vat': '2552977145',
}

# Listed in RTL reading order: the first item sits on the right.
FILTERS = [('Date from', '01/11/2026', 'من تاريخ'), ('Date to', '20/11/2026', 'إلى تاريخ'), ('Direction', 'كلاهما', 'اتجاه المعاملة')]

# (key, Arabic title, English subtitle, width or None to size by content, nowrap)
MOVEMENT_COLUMNS = [
    ('voucher', 'رقم السند', 'Voucher No.', None, True),
    ('operation', 'نوع العملية', 'Operation', None, True),
    ('date', 'التاريخ والوقت', 'Date & Time', None, True),
    ('description', 'البيان / الغرض', 'Description', None, False),
    ('method', 'طريقة الدفع', 'Payment Method', None, False),
    ('direction', 'الاتجاه', 'Direction', None, True),
    ('amount', 'المبلغ', 'Amount', None, True),
    ('account', 'البنك / الصندوق', 'Bank / Cashbox', None, False),
    ('user', 'المستخدم', 'User', None, True),
]

MOVEMENTS = [
    {'voucher': '000004', 'operation': 'سند قبض', 'date': date_time('14/11/2026', '12:47 AM'), 'description': 'دفعة للحجز رقم\n(RES-A-000001)', 'method': 'الدفع نقدًا', 'direction': 'داخل', 'amount': '200.00 ﷼', 'account': 'الصندوق', 'user': 'عبدالله العيدروس'},
    {'voucher': '000003', 'operation': 'سند قبض', 'date': date_time('13/11/2026', '11:55 PM'), 'description': 'دفعة للحجز رقم\n(RES-A-000001)', 'method': 'الدفع نقدًا', 'direction': 'داخل', 'amount': '100.00 ﷼', 'account': 'الصندوق', 'user': 'عبدالله العيدروس'},
    {'voucher': '000002', 'operation': 'سند قبض', 'date': date_time('13/11/2026', '11:54 PM'), 'description': 'دفعة للحجز رقم\n(RES-A-000001)', 'method': 'دفع بواسطة طرف ثالث', 'direction': 'داخل', 'amount': '100.00 ﷼', 'account': '—', 'user': 'عبدالله العيدروس'},
    {'voucher': '000001', 'operation': 'سند قبض', 'date': date_time('13/11/2026', '11:39 PM'), 'description': 'دفعة للحجز رقم\n(RES-A-000001)', 'method': 'تمارا', 'direction': 'داخل', 'amount': '100.00 ﷼', 'account': '—', 'user': 'عبدالله العيدروس'},
]

SUMMARY_COLUMNS = [
    ('method', 'طريقة الدفع', 'Method', '36%', False),
    ('count', 'عدد الحركات', 'Count', None, True),
    ('receipts', 'سندات القبض', 'Receipts', None, True),
    ('payments', 'سندات الصرف', 'Payments', None, True),
    ('net', 'الصافي', 'Net', None, True),
]
SUMMARY_ROWS = [
    {'method': 'الدفع نقدًا', 'count': '2', 'receipts': '300.00', 'payments': '0.00', 'net': '300.00'},
    {'method': 'تمارا', 'count': '1', 'receipts': '100.00', 'payments': '0.00', 'net': '100.00'},
    {'method': 'دفع بواسطة طرف ثالث', 'count': '1', 'receipts': '100.00', 'payments': '0.00', 'net': '100.00'},
]
SUMMARY_TOTAL = {'method': 'الإجمالي (﷼)', 'count': '4', 'receipts': '500.00', 'payments': '0.00', 'net': '500.00'}
METADATA = [('Printed by', 'عبدالله العيدروس', 'طبع بواسطة'), ('Printed at', '20/11/2026  01:02 PM', 'طبع في'), ('Postal Code', '34442', 'الرمز البريدي'), ('Email', '—', 'البريد الإلكتروني')]
