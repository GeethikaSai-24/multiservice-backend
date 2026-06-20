from django.urls import path
from .views import create_booking
from .views import get_booked_slots
from .views import get_user_bookings
from .views import cancel_booking
from .views import check_availability
from .views import hide_booking_from_user_history
from .views import reschedule_booking
urlpatterns = [
    path('', create_booking),
    path('slots/', get_booked_slots),
    path('user/', get_user_bookings),
    path('<int:booking_id>/cancel/', cancel_booking), 
    path('<int:booking_id>/hide/', hide_booking_from_user_history),
    path('<int:booking_id>/reschedule/', reschedule_booking),
    path('check-availability/', check_availability),
]
