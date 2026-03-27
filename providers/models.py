from django.db import models

class Provider(models.Model):
    name = models.CharField(max_length=100)

    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    description = models.TextField(blank=True, null=True)
    hero_image = models.URLField(blank=True, null=True)
    experience_years = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    rating = models.FloatField(default=4.5)

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    location = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class ProviderMedia(models.Model):
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name='media'
    )

    file = models.URLField()  # for now use URL (later we can use upload)
    
    media_type = models.CharField(
        max_length=10,
        choices=[
            ('image', 'Image'),
            ('video', 'Video'),
        ]
    )

    uploaded_by_customer = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.provider.name} - {self.media_type}"