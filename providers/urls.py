from django.urls import path
from .views import get_providers

urlpatterns = [
    path('', get_providers),
]