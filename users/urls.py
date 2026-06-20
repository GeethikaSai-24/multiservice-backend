from django.urls import path

from .views import (
    AdminCreateProviderAccountView,
    AdminDashboardView,
    AdminReviewRegistrationView,
    ForgotPasswordView,
    LoginView,
    MeView,
    RegisterView,
    ResetPasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),
    path("me/", MeView.as_view()),
    path("admin/dashboard/", AdminDashboardView.as_view()),
    path("admin/providers/create-account/", AdminCreateProviderAccountView.as_view()),
    path("admin/registrations/<int:user_id>/review/", AdminReviewRegistrationView.as_view()),
]
