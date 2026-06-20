from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Service, ServiceCategory
from .serializers import ServiceCategorySerializer, ServiceSerializer


class ServiceCategoryListView(APIView):
    def get(self, request):
        categories = ServiceCategory.objects.prefetch_related('services').all()
        serializer = ServiceCategorySerializer(categories, many=True)
        return Response(serializer.data)


def _ensure_admin(user):
    return getattr(user, 'role', '').upper() == 'ADMIN'


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_categories(request):
    if not _ensure_admin(request.user):
        return Response({'error': 'Admin access required'}, status=403)

    if request.method == 'GET':
        categories = ServiceCategory.objects.all().order_by('name')
        return Response(ServiceCategorySerializer(categories, many=True).data)

    serializer = ServiceCategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def admin_category_detail(request, category_id):
    if not _ensure_admin(request.user):
        return Response({'error': 'Admin access required'}, status=403)

    try:
        category = ServiceCategory.objects.get(id=category_id)
    except ServiceCategory.DoesNotExist:
        return Response({'error': 'Category not found'}, status=404)

    if request.method == 'DELETE':
        category.delete()
        return Response({'message': 'Category deleted'})

    serializer = ServiceCategorySerializer(category, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_services(request):
    if not _ensure_admin(request.user):
        return Response({'error': 'Admin access required'}, status=403)

    if request.method == 'GET':
        services = Service.objects.select_related('category').all().order_by('category__name', 'name')
        return Response(ServiceSerializer(services, many=True).data)

    serializer = ServiceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def admin_service_detail(request, service_id):
    if not _ensure_admin(request.user):
        return Response({'error': 'Admin access required'}, status=403)

    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=404)

    if request.method == 'DELETE':
        service.delete()
        return Response({'message': 'Service deleted'})

    serializer = ServiceSerializer(service, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)
