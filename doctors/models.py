from django.db import models
from providers.models import Provider


class DoctorProfile(models.Model):
    provider = models.OneToOneField(Provider, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=150)
    hospital_name = models.CharField(max_length=200)

    def __str__(self):
        return self.provider.name