from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Bill, BillPayment
from .forms import BillForm


@login_required
def bill_list(request):
    if request.method == 'POST':
        form = BillForm(request.POST, user=request.user)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.owner = request.user
            bill.save()
            return redirect('bill_list')
    else:
        form = BillForm(user=request.user)

    sort = request.GET.get('sort', 'due_date')
    valid_sorts = ['recipient', 'amount', 'due_date', 'payment_source', 'payment_type']
    if sort.lstrip('-') not in valid_sorts:
        sort = 'due_date'

    bills = Bill.objects.filter(owner=request.user).order_by(sort)

    totals_by_income = {}
    for bill in bills:
        key = bill.income.source
        totals_by_income[key] = totals_by_income.get(key, Decimal('0')) + bill.amount

    totals_list = sorted(
        [{'source': k, 'total': v} for k, v in totals_by_income.items()],
        key=lambda x: x['source']
    )
    grand_total = sum(totals_by_income.values(), Decimal('0'))

    return render(request, 'bills/bill_list.html', {
        'form': form,
        'bills': bills,
        'current_sort': sort,
        'totals_list': totals_list,
        'grand_total': grand_total,
    })


@login_required
def bill_delete(request, pk):
    bill = get_object_or_404(Bill, pk=pk, owner=request.user)
    if request.method == 'POST':
        bill.delete()
        return redirect('bill_list')
    return render(request, 'bills/bill_delete.html', {'bill': bill})


@login_required
def bill_edit(request, pk):
    bill = get_object_or_404(Bill, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = BillForm(request.POST, instance=bill, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('bill_list')
    else:
        form = BillForm(instance=bill, user=request.user)
    return render(request, 'bills/bill_edit.html', {'form': form, 'bill': bill})


@login_required
def bill_toggle_paid(request, pk):
    bill = get_object_or_404(Bill, pk=pk, owner=request.user)
    if request.method == 'POST':
        try:
            year = int(request.POST.get('year'))
            month = int(request.POST.get('month'))
        except (TypeError, ValueError):
            year, month = None, None

        if bill.is_recurring and year and month:
            payment, created = BillPayment.objects.get_or_create(bill=bill, year=year, month=month)
            if not created:
                payment.delete()
        else:
            bill.paid = not bill.paid
            bill.save()

        next_url = request.POST.get('next') or 'cashflow_view'
        return redirect(next_url)
    return redirect('cashflow_view')