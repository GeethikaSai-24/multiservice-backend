from django.urls import path
from .views import get_reviews, add_review,delete_review,update_review

urlpatterns = [
    path('', get_reviews),
    path('add/', add_review),
     path('<int:review_id>/delete/', delete_review),
    path('<int:review_id>/update/', update_review),
]