from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Booking
from .serializers import BookingSerializer
from providers.models import ProviderUnavailableDate


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_booking(request):
    provider = request.data.get("provider")
    date = request.data.get("date")
    time = request.data.get("time")

    existing = Booking.objects.filter(
        provider_id=provider,
        date=date,
        time=time,
    ).exclude(status='cancelled').exists()
    if existing:
        return Response({"error": "This slot is already booked"}, status=400)

    if ProviderUnavailableDate.objects.filter(provider_id=provider, date=date).exists():
        return Response(
            {"error": "The provider is marked unavailable on this date."},
            status=400,
        )

    booking_data = request.data.copy()
    booking_data["user"] = request.user.id
    serializer = BookingSerializer(data=booking_data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_bookings(request):
    bookings = Booking.objects.filter(
        user=request.user,
        hidden_for_user=False,
    ).order_by("-date", "-time")
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_booked_slots(request):
    provider_id = request.GET.get("provider")
    date = request.GET.get("date")

    if ProviderUnavailableDate.objects.filter(provider_id=provider_id, date=date).exists():
        return Response({"unavailable": True, "slots": []})

    bookings = Booking.objects.filter(
        provider_id=provider_id,
        date=date,
    ).exclude(status='cancelled')
    booked_times = [booking.time.strftime("%H:%M") for booking in bookings]
    return Response({"unavailable": False, "slots": booked_times})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    if booking.status == "cancelled":
        return Response({"error": "Booking is already cancelled"}, status=400)

    booking.status = "cancelled"
    booking.cancellation_source = "customer"
    if booking.payment_status == "paid":
        booking.refund_status = "pending"
    booking.save()
    return Response(
        {
            "message": "Booking cancelled successfully",
            "refund_status": booking.refund_status,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def hide_booking_from_user_history(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    booking.hidden_for_user = True
    booking.save(update_fields=["hidden_for_user"])
    return Response({"message": "Booking removed from your history"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reschedule_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    if booking.status in ["cancelled", "completed"]:
        return Response(
            {"error": "Only active bookings can be rescheduled"},
            status=400,
        )

    new_date = request.data.get("date")
    new_time = request.data.get("time")

    if not new_date or not new_time:
        return Response({"error": "Date and time are required"}, status=400)

    if ProviderUnavailableDate.objects.filter(
        provider=booking.provider,
        date=new_date,
    ).exists():
        return Response(
            {"error": "The provider marked this day as unavailable."},
            status=400,
        )

    existing = Booking.objects.filter(
        provider=booking.provider,
        date=new_date,
        time=new_time,
        hidden_for_provider=False,
    ).exclude(id=booking.id).exclude(status="cancelled").exists()

    if existing:
        return Response({"error": "This slot is already booked"}, status=400)

    booking.date = new_date
    booking.time = new_time
    booking.status = "pending"
    booking.save(update_fields=["date", "time", "status"])
    serializer = BookingSerializer(booking)
    return Response(
        {
            "message": "Booking rescheduled successfully",
            "booking": serializer.data,
        }
    )


@api_view(["GET"])
def check_availability(request):
    provider_id = request.GET.get("provider")
    date = request.GET.get("date")

    if ProviderUnavailableDate.objects.filter(provider_id=provider_id, date=date).exists():
        return Response(
            {
                "available": False,
                "message": "The provider marked this day as unavailable.",
            }
        )

    bookings = Booking.objects.filter(provider_id=provider_id, date=date).exclude(
        status='cancelled'
    )
    if bookings.count() >= 5:
        return Response({"available": False, "message": "No slots left for this day."})

    return Response({"available": True})
