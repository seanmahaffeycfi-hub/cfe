from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class Income(models.Model):
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('biweekly', 'Biweekly'),
        ('semimonthly', 'Semimonthly'),        
        ('monthly', 'Monthly'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_deduction_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    frequency = models.CharField(max_length=12, choices=FREQUENCY_CHOICES)
    start_pay_date = models.DateField(help_text="The first known/anchor pay date")

    class Meta:
        ordering = ['source']

    def __str__(self):
        return f"{self.source} ({self.get_frequency_display()})"
    
    @property
    def net_amount(self):
        return self.amount * (1- (self.tax_deduction_percent / 100))

    def get_pay_dates_in_range(self, range_start, range_end):
        """Return a sorted list of pay dates that fall between range_start and range_end (inclusive)."""
        dates = []

        if self.frequency in ('weekly', 'biweekly'):
            step = timedelta(days=7 if self.frequency == 'weekly' else 14)
            current = self.start_pay_date
            if current < range_start:
                periods_to_skip = (range_start - current) // step
                current = current + (step * periods_to_skip)
            while current <= range_end:
                if current >= range_start:
                    dates.append(current)
                current += step

        elif self.frequency == 'semimonthly':
            month_cursor = range_start.replace(day=1)
            while month_cursor <= range_end:
                first_day = self.start_pay_date.day if self.start_pay_date.day <= 28 else 28
                day_one = month_cursor.replace(day=first_day)
                day_two = day_one + timedelta(days=15)
                for d in (day_one, day_two):
                    if range_start <= d <= range_end:
                        dates.append(d)
                month_cursor += relativedelta(months=1)

        elif self.frequency == 'monthly':
            current = self.start_pay_date
            while current < range_start:
                current += relativedelta(months=1)
            while current <= range_end:
                dates.append(current)
                current += relativedelta(months=1)

        return sorted(dates)