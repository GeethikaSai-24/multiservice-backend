from rest_framework import serializers
from .models import Booking
from providers.models import Provider

class BookingSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'