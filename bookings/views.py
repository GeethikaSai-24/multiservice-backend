from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Booking
from .serializers import BookingSerializer

@api_view(['POST'])
def create_booking(request):
    provider = request.data.get('provider')
    date = request.data.get('date')
    time = request.data.get('time')

    # 🔥 CHECK FOR DUPLICATE BOOKING
    existing = Booking.objects.filter(
        provider_id=provider,
        date=date,
        time=time
    ).exists()

    if existing:
        return Response(
            {"error": "This slot is already booked"},
            status=400
        )

    serializer = BookingSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)
@api_view(['GET'])
def get_user_bookings(request):
    user_id = request.GET.get('user')

    bookings = Booking.objects.filter(user_id=user_id).order_by('-date')

    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_booked_slots(request):
    provider_id = request.GET.get('provider')
    date = request.GET.get('date')

    bookings = Booking.objects.filter(
        provider_id=provider_id,
        date=date
    )

    booked_times = [b.time.strftime("%H:%M") for b in bookings]

    return Response(booked_times)
@api_view(['POST'])
def cancel_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)

        # 🔥 update status
        booking.status = 'cancelled'
        booking.save()

        return Response({"message": "Booking cancelled successfully"})
    
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)
@api_view(['GET'])
def check_availability(request):
    provider_id = request.GET.get('provider')
    date = request.GET.get('date')

    bookings = Booking.objects.filter(
        provider_id=provider_id,
        date=date
    )

    # simple rule: max 5 bookings per day
    if bookings.count() >= 5:
        return Response({"available": False})

    return Response({"available": True})