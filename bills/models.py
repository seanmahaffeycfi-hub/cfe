from django.db import models
from django.contrib.auth.models import User
from income.models import Income
from datetime import date
from calendar import monthrange


class Bill(models.Model):
    SOURCE_CHOICES = [
        ('usaa', 'USAA'),
        ('usaa_savings', 'USAA Savings'),
        ('chase', 'Chase'),
        ('capone', 'CapOne'),
    ]
    TYPE_CHOICES = [
        ('auto', 'Auto'),
        ('manual', 'Manual'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(help_text="First/anchor due date")
    payment_source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    payment_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    income = models.ForeignKey(Income, on_delete=models.PROTECT, related_name='bills')
    paid = models.BooleanField(default=False, help_text="Used only for one-time (non-recurring) bills")
    is_recurring = models.BooleanField(default=True, help_text="Repeats monthly on the same day. Uncheck for a one-time bill.")
    recurrence_end_date = models.DateField(null=True, blank=True, help_text="Optional. Recurring bill stops after this date (e.g. final loan payment).")

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.recipient} - ${self.amount}"

    def get_due_date_for_month(self, year, month):
        """Return this bill's due date within the given year/month, or None if it doesn't apply."""
        last_day = monthrange(year, month)[1]
        day = min(self.due_date.day, last_day)
        candidate = date(year, month, day)

        if not self.is_recurring:
            if self.due_date.year == year and self.due_date.month == month:
                return self.due_date
            return None

        if (year, month) < (self.due_date.year, self.due_date.month):
            return None
        if self.recurrence_end_date and candidate > self.recurrence_end_date:
            return None
        return candidate

    def is_paid_for(self, year, month):
        if not self.is_recurring:
            return self.paid
        return self.payments.filter(year=year, month=month).exists()


class BillPayment(models.Model):
    """Marks a single recurring bill as paid for one specific month. Presence of a row = paid."""
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
    year = models.IntegerField()
    month = models.IntegerField()

    class Meta:
        unique_together = ('bill', 'year', 'month')