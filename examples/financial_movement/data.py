"""Prepared display data transcribed from the supplied financial movement PDF."""

BRANDING = {
    'name_en': 'Alahqaf Hotel', 'name_ar': 'فندق الاحقاف',
    'location_en': 'Saudi Arabia - Khobar', 'location_ar': 'السعودية (المملكة العربية) - الخبر',
    'address_en': 'EKJA4034, 4034 11th St, 6997, Madinat Al Umal, Al Khobar 34442, Saudi Arabia',
    'address_ar': 'EKJA4034، 4034 الشارع الحادي عشر، 6997، مدينة العمال، الخبر 34442، السعودية',
    'cr': '2552977145', 'vat': '2552977145',
}

FILTERS = [('Date to', '20/11/2026', 'إلى تاريخ'), ('Date from', '01/11/2026', 'من تاريخ'), ('', '', ''), ('Direction', 'كلاهما', 'اتجاه المعاملة')]

MOVEMENT_COLUMNS = [
    ('voucher', 'رقم السند\nVoucher Number', '9%'),
    ('operation', 'نوع العملية\nOperation Type', '10%'),
    ('datetime', 'التاريخ والوقت\nDate & Time', '11%'),
    ('description', 'البيان / الغرض\nDescription / Purpose', '21%'),
    ('method', 'طريقة الدفع\nPayment Method', '15%'),
    ('direction', 'الاتجاه\nDirection', '8%'),
    ('amount', 'المبلغ\nAmount', '9%'),
    ('account', 'البنك / الصندوق\nBank / Cashbox', '9%'),
    ('user', 'المستخدم\nUser', '8%'),
]

MOVEMENTS = [
    {'voucher': '000004', 'operation': 'سند قبض', 'datetime': '14/11/2026\nAM 12:47', 'description': 'دفعة للحجز رقم\n(RES-A-000001)', 'method': 'الدفع نقدًا', 'direction': 'داخل', 'amount': '⃁ 200.00', 'account': 'الصندوق', 'user': 'عبدالله العيدروس'},
    {'voucher': '000003', 'operation': 'سند قبض', 'datetime': '13/11/2026\nPM 11:55', 'description': 'دفعة للحجز رقم\n(RES-A-000001)', 'method': 'الدفع نقدًا', 'direction': 'داخل', 'amount': '⃁ 100.00', 'account': 'الصندوق', 'user': 'عبدالله العيدروس'},
    {'voucher': '000002', 'operation': 'سند قبض', 'datetime': '13/11/2026\nPM 11:54', 'description': 'دفعة للحجز رقم\n(RES-A-000001)', 'method': 'دفع بواسطة طرف ثالث', 'direction': 'داخل', 'amount': '⃁ 100.00', 'account': '—', 'user': 'عبدالله العيدروس'},
    {'voucher': '000001', 'operation': 'سند قبض', 'datetime': '13/11/2026\nPM 11:39', 'description': 'دفعة للحجز رقم\n(RES-A-000001)', 'method': 'تمارا', 'direction': 'داخل', 'amount': '⃁ 100.00', 'account': '—', 'user': 'عبدالله العيدروس'},
]

SUMMARY_COLUMNS = [('method', 'طريقة الدفع\nMethod', '38%'), ('count', 'عدد الحركات\nCount', '15.5%'), ('receipts', 'سندات القبض\nReceipts', '15.5%'), ('payments', 'سندات الصرف\nPayments', '15.5%'), ('net', 'الصافي\nNet', '15.5%')]
SUMMARY_ROWS = [
    {'method': 'الدفع نقدًا', 'count': '2', 'receipts': '300.00', 'payments': '0.00', 'net': '300.00'},
    {'method': 'تمارا', 'count': '1', 'receipts': '100.00', 'payments': '0.00', 'net': '100.00'},
    {'method': 'دفع بواسطة طرف ثالث', 'count': '1', 'receipts': '100.00', 'payments': '0.00', 'net': '100.00'},
]
SUMMARY_TOTAL = {'method': 'الإجمالي (⃁)', 'count': '4', 'receipts': '500.00', 'payments': '0.00', 'net': '500.00'}
METADATA = [('Printed by', 'عبدالله العيدروس', 'طبع بواسطة'), ('Printed at', 'PM 01:02 20/11/2026', 'طبع في'), ('Postal Code', '34442', 'الرمز البريدي'), ('Email', '—', 'البريد الإلكتروني')]
