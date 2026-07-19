from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from calendar import monthrange
from decimal import Decimal
from income.models import Income
from bills.models import Bill

ACCOUNT_ORDER = [
    ('usaa', 'USAA'),
    ('chase', 'Chase'),
    ('usaa_savings', 'USAA Savings'),
    ('capone', 'CapOne'),
]


def _get_month_range(request):
    today = date.today()
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except ValueError:
        year, month = today.year, today.month
    range_start = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    range_end = date(year, month, last_day)
    return year, month, range_start, range_end, last_day


def _month_nav(year, month):
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1
    return prev_year, prev_month, next_year, next_month


def _bills_due_this_month(year, month):
    """Expand every bill (recurring or one-time) into its due date for this specific month, if any."""
    all_bills = Bill.objects.all().select_related('income')
    result = []
    for bill in all_bills:
        due = bill.get_due_date_for_month(year, month)
        if due:
            result.append((bill, due))
    return result


@login_required
def cashflow_view(request):
    year, month, range_start, range_end, last_day = _get_month_range(request)

    bills_this_month = _bills_due_this_month(year, month)

    account_totals = {code: Decimal('0') for code, label in ACCOUNT_ORDER}
    for bill, due in bills_this_month:
        account_totals[bill.payment_source] += bill.amount

    entries = []
    incomes = Income.objects.all()
    for income in incomes:
        for pay_date in income.get_pay_dates_in_range(range_start, range_end):
            entries.append({
                'date': pay_date,
                'kind': 'income',
                'owner': income.source,
                'description': income.source,
                'income_amount': income.net_amount,
                'bill_amount': None,
                'bill_pk': None,
                'paid': None,
                'payment_source': None,
                'edit_url': f'/income/{income.pk}/edit/',
                'delete_url': f'/income/{income.pk}/delete/',
            })

    for bill, due in bills_this_month:
        entries.append({
            'date': due,
            'kind': 'bill',
            'owner': bill.income.source,
            'description': bill.recipient,
            'income_amount': None,
            'bill_amount': bill.amount,
            'bill_pk': bill.pk,
            'paid': bill.is_paid_for(year, month),
            'payment_source': bill.payment_source,
            'edit_url': f'/bills/{bill.pk}/edit/',
            'delete_url': f'/bills/{bill.pk}/delete/',
        })

    entries.sort(key=lambda e: (e['date'], e['kind']))

    running = {code: Decimal('0') for code, label in ACCOUNT_ORDER}
    for e in entries:
        if e['kind'] == 'bill' and not e['paid']:
            running[e['payment_source']] += e['bill_amount']
        e['running'] = dict(running)

    sort = request.GET.get('sort', 'date')
    if sort == '-date':
        entries.sort(key=lambda e: e['date'], reverse=True)

    prev_year, prev_month, next_year, next_month = _month_nav(year, month)

    context = {
        'entries': entries,
        'account_order': ACCOUNT_ORDER,
        'account_totals': account_totals,
        'month_label': range_start.strftime('%B %Y'),
        'year': year,
        'month': month,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'current_sort': sort,
        'query_string': f'year={year}&month={month}',
    }
    return render(request, 'cashflow/cashflow_view.html', context)


@login_required
def cashflow_by_account_view(request):
    year, month, range_start, range_end, last_day = _get_month_range(request)

    mid_day = min(15, last_day)
    period1_start, period1_end = range_start, date(year, month, mid_day)
    period2 = (date(year, month, mid_day + 1), range_end) if mid_day < last_day else None

    incomes = Income.objects.all()
    bills_with_due = _bills_due_this_month(year, month)

    def blank_row(owner):
        return {'owner': owner, 'total_income': Decimal('0'), 'usaa': Decimal('0'),
                'usaa_savings': Decimal('0'), 'chase': Decimal('0'), 'capone': Decimal('0')}

    def build_income_summary(period_start, period_end):
        rows = {}
        for income in incomes:
            for pay_date in income.get_pay_dates_in_range(period_start, period_end):
                rows.setdefault(income.source, blank_row(income.source))
                rows[income.source]['total_income'] += income.net_amount

        for bill, due in bills_with_due:
            if period_start <= due <= period_end:
                key = bill.income.source
                rows.setdefault(key, blank_row(key))
                rows[key][bill.payment_source] += bill.amount

        result = []
        for key in sorted(rows.keys()):
            row = rows[key]
            row['remaining'] = row['total_income'] - row['usaa'] - row['usaa_savings'] - row['chase'] - row['capone']
            result.append(row)
        return result

    period1_summary = build_income_summary(period1_start, period1_end)
    period2_summary = build_income_summary(period2[0], period2[1]) if period2 else []

    account_sections = []
    for code, label in ACCOUNT_ORDER:
        account_bills = sorted(
            [(bill, due, bill.is_paid_for(year, month)) for bill, due in bills_with_due if bill.payment_source == code],
            key=lambda triple: triple[1]
        )
        account_sections.append({'code': code, 'label': label, 'bills': account_bills})

    prev_year, prev_month, next_year, next_month = _month_nav(year, month)

    context = {
        'month_label': range_start.strftime('%B %Y'),
        'year': year,
        'month': month,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'period1_label': f"{period1_start.strftime('%b %d')} - {period1_end.strftime('%b %d')}",
        'period2_label': f"{period2[0].strftime('%b %d')} - {period2[1].strftime('%b %d')}" if period2 else None,
        'period1_summary': period1_summary,
        'period2_summary': period2_summary,
        'account_sections': account_sections,
    }
    return render(request, 'cashflow/cashflow_by_account.html', context)