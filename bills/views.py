from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Bill
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
    return render(request, 'bills/bill_list.html', {'form': form, 'bills': bills, 'current_sort': sort})


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