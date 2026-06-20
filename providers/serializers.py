from rest_framework import serializers

from bookings.serializers import BookingSerializer

from .models import Provider, ProviderMedia


class ProviderMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderMedia
        fields = '__all__'


class ProviderSerializer(serializers.ModelSerializer):
    media = ProviderMediaSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='service.category.name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Provider
        fields = [
            'id',
            'name',
            'description',
            'hero_image',
            'experience_years',
            'rating',
            'price',
            'location',
            'is_available',
            'service',
            'service_name',
            'media',
            'category_name',
            'phone_number',
            'user_name',
        ]
        read_only_fields = ['rating', 'media', 'category_name', 'service_name', 'user_name']


class ProviderDashboardSummarySerializer(serializers.Serializer):
    today_bookings = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    cancelled_bookings = serializers.IntegerField()
    rating = serializers.FloatField()
    monthly_earnings = serializers.FloatField()


class ProviderDashboardSerializer(serializers.Serializer):
    provider = ProviderSerializer()
    summary = ProviderDashboardSummarySerializer()
    recent_bookings = serializers.ListField(child=serializers.DictField())
