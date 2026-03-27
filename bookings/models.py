from django.db import models
from providers.models import Provider
from users.models import User  # adjust if needed

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    address = models.TextField(blank=True,null=True)
    phone_number = models.CharField(max_length=15,blank=True,null=True)
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('completed', 'Completed'),
        ],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    consultation_type = models.CharField(
    max_length=10,
    choices=[('online', 'Online'), ('offline', 'Offline')],
    default='offline'
)
    def __str__(self):
        return f"{self.user} - {self.provider} - {self.date} {self.time}"
    