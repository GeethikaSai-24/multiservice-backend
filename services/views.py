from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ServiceCategory
from .serializers import ServiceCategorySerializer


class ServiceCategoryListView(APIView):
    def get(self, request):
        categories = ServiceCategory.objects.prefetch_related('services').all()
        serializer = ServiceCategorySerializer(categories, many=True)
        return Response(serializer.data)