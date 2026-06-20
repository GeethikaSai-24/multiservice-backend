from django.db import models

from providers.models import Provider
from users.models import User


class Booking(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online'),
        ('cash', 'Pay at Service'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('refunded', 'Refunded'),
    ]
    REFUND_STATUS_CHOICES = [
        ('not_applicable', 'Not Applicable'),
        ('pending', 'Pending'),
        ('processed', 'Processed'),
    ]
    CANCELLATION_SOURCE_CHOICES = [
        ('customer', 'Customer'),
        ('provider', 'Provider'),
        ('admin', 'Admin'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    consultation_type = models.CharField(
        max_length=10,
        choices=[('online', 'Online'), ('offline', 'Offline')],
        default='offline',
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
    )
    refund_status = models.CharField(
        max_length=20,
        choices=REFUND_STATUS_CHOICES,
        default='not_applicable',
    )
    cancellation_source = models.CharField(
        max_length=20,
        choices=CANCELLATION_SOURCE_CHOICES,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    hidden_for_user = models.BooleanField(default=False)
    hidden_for_provider = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.provider} - {self.date} {self.time}"
