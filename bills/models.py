from django.db import models
from django.contrib.auth.models import User
from income.models import Income


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
    due_date = models.DateField()
    payment_source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    payment_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    income = models.ForeignKey(Income, on_delete=models.CASCADE, related_name='bills')

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.recipient} - ${self.amount}"