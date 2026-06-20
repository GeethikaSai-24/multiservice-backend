from django.urls import path

from .views import (
    ServiceCategoryListView,
    admin_categories,
    admin_category_detail,
    admin_service_detail,
    admin_services,
)

urlpatterns = [
    path('categories/', ServiceCategoryListView.as_view()),
    path('admin/categories/', admin_categories),
    path('admin/categories/<int:category_id>/', admin_category_detail),
    path('admin/services/', admin_services),
    path('admin/services/<int:service_id>/', admin_service_detail),
]
