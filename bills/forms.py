from django import forms
from .models import Bill


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['recipient', 'amount', 'due_date', 'payment_source', 'payment_type', 'income']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['income'].queryset = self.fields['income'].queryset.model.objects.filter(owner=user)