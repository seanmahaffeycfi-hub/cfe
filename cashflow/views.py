from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from calendar import monthrange
from income.models import Income
from bills.models import Bill


@login_required
def cashflow_view(request):
    today = date.today()
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except ValueError:
        year, month = today.year, today.month

    range_start = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    range_end = date(year, month, last_day)

    entries = []

    incomes = Income.objects.filter(owner=request.user)
    for income in incomes:
        for pay_date in income.get_pay_dates_in_range(range_start, range_end):
            entries.append({
                'date': pay_date,
                'type': 'Income',
                'description': income.source,
                'amount': income.net_amount,
                'edit_url': f'/income/{income.pk}/edit/',
                'delete_url': f'/income/{income.pk}/delete/',
            })

    bills = Bill.objects.filter(owner=request.user, due_date__gte=range_start, due_date__lte=range_end)
    for bill in bills:
        entries.append({
            'date': bill.due_date,
            'type': 'Bill',
            'description': f"{bill.recipient} ({bill.get_payment_source_display()}, {bill.get_payment_type_display()})",
            'amount': -bill.amount,
            'edit_url': f'/bills/{bill.pk}/edit/',
            'delete_url': f'/bills/{bill.pk}/delete/',
        })

    # Always compute the running balance in true chronological order first,
    # THEN re-sort for display so the balance column stays mathematically correct
    # no matter which column the user clicks to sort by.
    entries.sort(key=lambda e: e['date'])
    running_balance = 0
    for e in entries:
        running_balance += e['amount']
        e['balance'] = running_balance

    sort = request.GET.get('sort', 'date')
    reverse = sort.startswith('-')
    sort_key = sort.lstrip('-')
    valid_sorts = ['date', 'type', 'description', 'amount', 'balance']
    if sort_key not in valid_sorts:
        sort_key = 'date'
    entries.sort(key=lambda e: e[sort_key], reverse=reverse)

    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    context = {
        'entries': entries,
        'month_label': range_start.strftime('%B %Y'),
        'year': year,
        'month': month,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'current_sort': sort,
    }
    return render(request, 'cashflow/cashflow_view.html', context)