from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from decimal import Decimal
from .models import Income
from .forms import IncomeForm


@login_required
def income_list(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.owner = request.user
            income.save()
            return redirect('income_list')
    else:
        form = IncomeForm()

    incomes = Income.objects.all()

    summary = {}
    for income in incomes:
        key = income.source
        if key not in summary:
            summary[key] = {'gross': Decimal('0'), 'net': Decimal('0')}
        summary[key]['gross'] += income.amount
        summary[key]['net'] += income.net_amount

    summary_list = sorted(
        [{'source': k, 'gross': v['gross'], 'net': v['net']} for k, v in summary.items()],
        key=lambda x: x['source']
    )
    total_gross = sum((i.amount for i in incomes), Decimal('0'))
    total_net = sum((i.net_amount for i in incomes), Decimal('0'))

    return render(request, 'income/income_list.html', {
        'form': form,
        'incomes': incomes,
        'summary_list': summary_list,
        'total_gross': total_gross,
        'total_net': total_net,
    })


@login_required
def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk)
    if request.method == 'POST':
        try:
            income.delete()
        except ProtectedError:
            return render(request, 'income/income_delete_blocked.html', {'income': income})
        return redirect('income_list')
    return render(request, 'income/income_delete.html', {'income': income})


@login_required
def income_edit(request, pk):
    income = get_object_or_404(Income, pk=pk)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            return redirect('income_list')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'income/income_edit.html', {'form': form, 'income': income})