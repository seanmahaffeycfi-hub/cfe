from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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
        income.delete()
        return redirect('income_list')
    return render(request, 'income/income_delete.html', {'income': income})