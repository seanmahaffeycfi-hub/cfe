from django import forms
from .models import Bill


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['recipient', 'amount', 'due_date', 'payment_source', 'payment_type', 'income', 'is_recurring', 'recurrence_end_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'recurrence_end_date': forms.DateInput(attrs={'type': 'date'}),
            'recipient': forms.TextInput(attrs={'autofocus': True}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['due_date'].label = 'First Due Date'
        self.fields['is_recurring'].label = 'Recurring Monthly'
        self.fields['recurrence_end_date'].label = 'Ends After (optional)'
        self.fields['recurrence_end_date'].required = False