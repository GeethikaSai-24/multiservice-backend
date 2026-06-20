from django.urls import path

from .views import (
    admin_manage_providers,
    admin_update_provider,
    get_my_provider_dashboard,
    get_providers,
    hide_provider_booking_history,
    manage_my_provider_profile,
    manage_provider_unavailable_dates,
    remove_provider_unavailable_date,
    update_provider_booking_status,
)

urlpatterns = [
    path('me/profile/', manage_my_provider_profile),
    path('me/dashboard/', get_my_provider_dashboard),
    path('me/unavailable-dates/', manage_provider_unavailable_dates),
    path('me/unavailable-dates/<int:item_id>/', remove_provider_unavailable_date),
    path('bookings/<int:booking_id>/status/', update_provider_booking_status),
    path('bookings/<int:booking_id>/hide/', hide_provider_booking_history),
    path('admin/manage/', admin_manage_providers),
    path('admin/<int:provider_id>/', admin_update_provider),
    path('', get_providers),
]
