from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from bookings.models import Booking
from providers.models import Provider
from services.models import Service, ServiceCategory

from .models import User
from .serializers import (
    AdminCreateProviderAccountSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserProfileSerializer,
)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            if user.role in {'PROVIDER', 'DOCTOR'}:
                return Response(
                    {
                        "message": "Registration submitted. Your account will be available after admin approval.",
                        "user": UserProfileSerializer(user).data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {
                    "message": "User registered successfully",
                    "user": UserProfileSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "message": "Login successful",
                    "user": UserProfileSerializer(user).data,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]

            try:
                User.objects.get(email=email)
                return Response({"message": "User verified. Proceed to reset password"})
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)

        return Response(serializer.errors, status=400)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            new_password = serializer.validated_data["new_password"]

            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password reset successful"})
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)

        return Response(serializer.errors, status=400)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'ADMIN':
            return Response({'error': 'Admin access required'}, status=403)

        linked_providers = Provider.objects.select_related('user', 'service').filter(user__isnull=False).order_by('name')
        unlinked_providers = Provider.objects.select_related('service').filter(user__isnull=True).order_by('name')
        pending_registrations = User.objects.filter(
            role__in=['PROVIDER', 'DOCTOR'],
            approval_status='PENDING',
        ).order_by('-created_at')
        users = User.objects.order_by('-created_at')
        bookings = Booking.objects.select_related('user', 'provider').order_by('-created_at')
        pending_bookings = bookings.filter(status='pending')

        return Response(
            {
                'stats': {
                    'users': User.objects.count(),
                    'providers': Provider.objects.count(),
                    'linked_providers': linked_providers.count(),
                    'unlinked_providers': unlinked_providers.count(),
                    'pending_provider_registrations': pending_registrations.count(),
                    'bookings': Booking.objects.count(),
                    'services': Service.objects.count(),
                    'categories': ServiceCategory.objects.count(),
                    'pending_bookings': Booking.objects.filter(status='pending').count(),
                },
                'pending_registrations': [
                    {
                        'id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'email': user.email,
                        'phone': user.phone,
                        'role': user.role,
                        'approval_status': user.approval_status,
                        'provider_location': getattr(getattr(user, 'provider_profile', None), 'location', ''),
                        'provider_description': getattr(getattr(user, 'provider_profile', None), 'description', ''),
                        'experience_years': getattr(getattr(user, 'provider_profile', None), 'experience_years', None),
                    }
                    for user in pending_registrations[:30]
                ],
                'users': [
                    {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role,
                        'approval_status': user.approval_status,
                        'phone': user.phone,
                    }
                    for user in users[:50]
                ],
                'bookings': [
                    {
                        'id': booking.id,
                        'user_name': booking.user.username,
                        'provider_name': booking.provider.name,
                        'date': booking.date.isoformat(),
                        'time': booking.time.strftime('%H:%M'),
                        'status': booking.status,
                        'payment_status': booking.payment_status,
                    }
                    for booking in bookings[:50]
                ],
                'pending_bookings_list': [
                    {
                        'id': booking.id,
                        'user_name': booking.user.username,
                        'provider_name': booking.provider.name,
                        'date': booking.date.isoformat(),
                        'time': booking.time.strftime('%H:%M'),
                        'status': booking.status,
                        'payment_status': booking.payment_status,
                    }
                    for booking in pending_bookings[:30]
                ],
                'linked_providers': [
                    {
                        'id': provider.id,
                        'name': provider.name,
                        'location': provider.location,
                        'service_name': provider.service.name if provider.service else None,
                        'username': provider.user.username if provider.user else None,
                        'role': provider.user.role if provider.user else None,
                        'approval_status': provider.user.approval_status if provider.user else None,
                    }
                    for provider in linked_providers[:20]
                ],
                'unlinked_providers': [
                    {
                        'id': provider.id,
                        'name': provider.name,
                        'location': provider.location,
                        'service_name': provider.service.name if provider.service else None,
                        'phone_number': provider.phone_number,
                    }
                    for provider in unlinked_providers[:30]
                ],
            }
        )


class AdminCreateProviderAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'ADMIN':
            return Response({'error': 'Admin access required'}, status=403)

        serializer = AdminCreateProviderAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            provider = Provider.objects.get(id=data['provider_id'])
        except Provider.DoesNotExist:
            return Response({'error': 'Provider not found'}, status=404)

        if provider.user_id is not None:
            return Response({'error': 'Provider already linked to an account'}, status=400)

        with transaction.atomic():
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                role=data['role'],
                phone=data.get('phone', '') or provider.phone_number,
                name=provider.name,
                approval_status='APPROVED',
            )
            provider.user = user
            if not provider.phone_number and data.get('phone'):
                provider.phone_number = data['phone']
            provider.save()

        return Response(
            {
                'message': 'Provider account created successfully',
                'user': UserProfileSerializer(user).data,
                'provider': {
                    'id': provider.id,
                    'name': provider.name,
                },
            },
            status=201,
        )


class AdminReviewRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if request.user.role != 'ADMIN':
            return Response({'error': 'Admin access required'}, status=403)

        decision = str(request.data.get('decision', '')).upper()
        if decision not in {'APPROVED', 'REJECTED'}:
            return Response({'error': 'Invalid decision'}, status=400)

        try:
            user = User.objects.get(id=user_id, role__in=['PROVIDER', 'DOCTOR'])
        except User.DoesNotExist:
            return Response({'error': 'Registration request not found'}, status=404)

        user.approval_status = decision
        user.save(update_fields=['approval_status'])

        return Response(
            {
                'message': f'{user.role.title()} registration {decision.lower()} successfully',
                'user': UserProfileSerializer(user).data,
            }
        )
