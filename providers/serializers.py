from rest_framework import serializers
from .models import Provider,ProviderMedia

class ProviderMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderMedia
        fields = '__all__'
class ProviderSerializer(serializers.ModelSerializer):
    media = ProviderMediaSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='service.category.name', read_only=True)
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
    'media',
    'category_name',
    'phone_number',
]
