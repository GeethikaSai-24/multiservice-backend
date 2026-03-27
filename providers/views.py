from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Provider
from .serializers import ProviderSerializer

@api_view(['GET'])
def get_providers(request):
    service_id = request.GET.get('service')
    location = request.GET.get('location')  # 🔥 NEW LINE

    providers = Provider.objects.all()

    # ✅ Filter by service
    if service_id:
        providers = providers.filter(service_id=service_id)

    # ✅ Filter by location
    if location:
        providers = providers.filter(location__icontains=location)

    serializer = ProviderSerializer(providers, many=True)
    return Response(serializer.data)