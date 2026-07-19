from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
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

    incomes = Income.objects.filter(owner=request.user)
    return render(request, 'income/income_list.html', {'form': form, 'incomes': incomes})


@login_required
def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk, owner=request.user)
    if request.method == 'POST':
        try:
            income.delete()
        except ProtectedError:
            return render(request, 'income/income_delete_blocked.html', {'income': income})
        return redirect('income_list')
    return render(request, 'income/income_delete.html', {'income': income})


@login_required
def income_edit(request, pk):
    income = get_object_or_404(Income, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            return redirect('income_list')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'income/income_edit.html', {'form': form, 'income': income})