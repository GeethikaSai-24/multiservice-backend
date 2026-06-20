from datetime import date
from decimal import Decimal

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bookings.models import Booking
from bookings.serializers import BookingSerializer

from .models import Provider, ProviderUnavailableDate
from .serializers import ProviderDashboardSerializer, ProviderSerializer


ALLOWED_PROVIDER_STATUSES = {'pending', 'confirmed', 'completed', 'cancelled'}


def _get_provider_for_user(user):
    if getattr(user, 'role', '').upper() not in {'PROVIDER', 'DOCTOR'}:
        return None
    provider = Provider.objects.filter(user=user).first()
    if provider is not None:
        return provider

    return Provider.objects.create(
        user=user,
        name=user.name or user.username,
        phone_number=getattr(user, 'phone', ''),
        is_available=False,
        description='Auto-created provider profile. Please complete your details.',
    )


def _ensure_admin(user):
    return getattr(user, 'role', '').upper() == 'ADMIN'


@api_view(['GET'])
def get_providers(request):
    service_id = request.GET.get('service')
    location = request.GET.get('location')

    providers = Provider.objects.all()
    if service_id:
        providers = providers.filter(service_id=service_id)
    if location:
        providers = providers.filter(location__icontains=location)

    serializer = ProviderSerializer(providers, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def manage_my_provider_profile(request):
    provider = _get_provider_for_user(request.user)
    if provider is None:
        return Response(
            {'error': 'No provider profile is linked to this account.'},
            status=404,
        )

    if request.method == 'GET':
        return Response(ProviderSerializer(provider).data)

    serializer = ProviderSerializer(provider, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_provider_dashboard(request):
    provider = _get_provider_for_user(request.user)
    if provider is None:
        return Response(
            {'error': 'No provider profile is linked to this account.'},
            status=404,
        )

    bookings = Booking.objects.filter(
        provider=provider,
        hidden_for_provider=False,
    ).order_by('-date', '-time')
    today = date.today()
    completed_bookings = bookings.filter(status='completed').count()
    cancelled_bookings = bookings.filter(status='cancelled').count()
    paid_completed_bookings = bookings.filter(status='completed').exclude(
        payment_status='refunded'
    )
    current_month_bookings = paid_completed_bookings.filter(
        date__year=today.year,
        date__month=today.month,
    )

    def booking_amount(booking):
        return float(booking.amount or provider.price or Decimal('0'))

    monthly_earnings = sum(booking_amount(booking) for booking in current_month_bookings)
    total_earnings = sum(booking_amount(booking) for booking in paid_completed_bookings)

    payload = {
        'provider': ProviderSerializer(provider).data,
        'summary': {
            'today_bookings': bookings.filter(date=today).count(),
            'pending_requests': bookings.filter(status='pending').count(),
            'completed_bookings': completed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'rating': provider.rating,
            'monthly_earnings': monthly_earnings,
            'total_earnings': total_earnings,
            'earnings_month_label': today.strftime('%B %Y'),
        },
        'recent_bookings': BookingSerializer(bookings[:10], many=True).data,
        'unavailable_dates': [
            {
                'id': item.id,
                'date': item.date.isoformat(),
                'reason': item.reason,
            }
            for item in provider.unavailable_dates.all()[:20]
        ],
    }

    return Response(payload)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_provider_booking_status(request, booking_id):
    provider = _get_provider_for_user(request.user)
    if provider is None:
        return Response({'error': 'No provider profile is linked to this account.'}, status=404)

    try:
        booking = Booking.objects.get(id=booking_id, provider=provider)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=404)

    refund_status = str(request.data.get('refund_status', '')).lower()
    if refund_status:
        if booking.status != 'cancelled':
            return Response(
                {'error': 'Refund can be updated only for cancelled bookings.'},
                status=400,
            )
        if refund_status not in {'pending', 'processed'}:
            return Response({'error': 'Invalid refund status'}, status=400)

        booking.refund_status = refund_status
        if refund_status == 'processed':
            booking.payment_status = 'refunded'
        booking.save(update_fields=['refund_status', 'payment_status'])
        return Response(BookingSerializer(booking).data)

    status_value = request.data.get('status', '').lower()
    if status_value not in ALLOWED_PROVIDER_STATUSES:
        return Response({'error': 'Invalid booking status'}, status=400)

    if booking.status == 'cancelled':
        return Response(
            {'error': 'Cancelled bookings can no longer be updated.'},
            status=400,
        )

    booking.status = status_value
    if status_value == 'cancelled':
        booking.cancellation_source = 'provider'
        if booking.payment_status == 'paid':
            booking.refund_status = 'pending'
    booking.save()
    return Response(BookingSerializer(booking).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_provider_unavailable_dates(request):
    provider = _get_provider_for_user(request.user)
    if provider is None:
        return Response({'error': 'No provider profile is linked to this account.'}, status=404)

    if request.method == 'GET':
        return Response(
            [
                {
                    'id': item.id,
                    'date': item.date.isoformat(),
                    'reason': item.reason,
                }
                for item in provider.unavailable_dates.all()
            ]
        )

    date_value = request.data.get('date')
    reason = request.data.get('reason', '')
    if not date_value:
        return Response({'error': 'Date is required'}, status=400)

    item, created = ProviderUnavailableDate.objects.get_or_create(
        provider=provider,
        date=date_value,
        defaults={'reason': reason},
    )
    if not created:
        return Response({'error': 'This date is already marked unavailable'}, status=400)

    return Response(
        {
            'id': item.id,
            'date': item.date.isoformat(),
            'reason': item.reason,
        },
        status=201,
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_provider_unavailable_date(request, item_id):
    provider = _get_provider_for_user(request.user)
    if provider is None:
        return Response({'error': 'No provider profile is linked to this account.'}, status=404)

    try:
        item = ProviderUnavailableDate.objects.get(id=item_id, provider=provider)
    except ProviderUnavailableDate.DoesNotExist:
        return Response({'error': 'Unavailable date not found'}, status=404)

    item.delete()
    return Response({'message': 'Unavailable date removed'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hide_provider_booking_history(request, booking_id):
    provider = _get_provider_for_user(request.user)
    if provider is None:
        return Response({'error': 'No provider profile is linked to this account.'}, status=404)

    try:
        booking = Booking.objects.get(id=booking_id, provider=provider)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=404)

    booking.hidden_for_provider = True
    booking.save(update_fields=['hidden_for_provider'])
    return Response({'message': 'Booking removed from provider history'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_manage_providers(request):
    if not _ensure_admin(request.user):
        return Response({'error': 'Admin access required'}, status=403)

    providers = Provider.objects.select_related('service', 'user').all().order_by('name')
    return Response(ProviderSerializer(providers, many=True).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def admin_update_provider(request, provider_id):
    if not _ensure_admin(request.user):
        return Response({'error': 'Admin access required'}, status=403)

    try:
        provider = Provider.objects.get(id=provider_id)
    except Provider.DoesNotExist:
        return Response({'error': 'Provider not found'}, status=404)

    serializer = ProviderSerializer(provider, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)
