from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from income.models import Income
from bills.models import Bill


@login_required
def export_data(request):
    incomes = Income.objects.all()
    bills = Bill.objects.all().select_related('income')

    data = {
        'exported_at': timezone.now().isoformat(),
        'username': request.user.username,
        'incomes': [
            {
                'source': i.source,
                'amount': str(i.amount),
                'tax_deduction_percent': str(i.tax_deduction_percent),
                'frequency': i.frequency,
                'start_pay_date': i.start_pay_date.isoformat(),
            }
            for i in incomes
        ],
        'bills': [
            {
                'recipient': b.recipient,
                'amount': str(b.amount),
                'due_date': b.due_date.isoformat(),
                'payment_source': b.payment_source,
                'payment_type': b.payment_type,
                'income_source': b.income.source,
                'is_recurring': b.is_recurring,
                'recurrence_end_date': b.recurrence_end_date.isoformat() if b.recurrence_end_date else None,
                'paid': b.paid,
            }
            for b in bills
        ],
    }

    response = JsonResponse(data, json_dumps_params={'indent': 2})
    filename = f"cfe_backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response