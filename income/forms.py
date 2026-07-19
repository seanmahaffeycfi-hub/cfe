from django import forms
from .models import Income

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['source', 'amount', 'tax_deduction_percent', 'frequency', 'start_pay_date']
        widgets = {
            'start_pay_date': forms.DateInput(attrs={'type': 'date'})
        }