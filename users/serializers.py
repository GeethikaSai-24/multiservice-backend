from django.contrib.auth import authenticate
from rest_framework import serializers

from providers.models import Provider

from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "name", "phone", "role", "approval_status"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='USER')
    name = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    service_category = serializers.CharField(required=False, allow_blank=True)
    service_name = serializers.CharField(required=False, allow_blank=True)
    specialization = serializers.CharField(required=False, allow_blank=True)
    hospital_name = serializers.CharField(required=False, allow_blank=True)
    experience = serializers.CharField(required=False, allow_blank=True)
    license_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "role",
            "phone",
            "name",
            "address",
            "city",
            "service_category",
            "service_name",
            "specialization",
            "hospital_name",
            "experience",
            "license_number",
        ]

    def validate_username(self, value):
        if len(value) < 4 or len(value) > 20:
            raise serializers.ValidationError(
                "Username must be 4 to 20 characters long."
            )
        if not value.replace('_', '').isalnum():
            raise serializers.ValidationError(
                "Username can use letters, numbers, and underscores only."
            )
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        if value.lower() == value or value.upper() == value:
            raise serializers.ValidationError(
                "Password must include both uppercase and lowercase letters."
            )
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must include at least one number.")
        if value.isalnum():
            raise serializers.ValidationError(
                "Password must include at least one special character."
            )
        return value

    def create(self, validated_data):
        role = validated_data.get("role", "USER")
        approval_status = 'PENDING' if role in {'PROVIDER', 'DOCTOR'} else 'APPROVED'
        display_name = validated_data.get("name") or validated_data["username"]
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=role,
            phone=validated_data.get("phone", ""),
            name=display_name,
            approval_status=approval_status,
        )

        if role in {'PROVIDER', 'DOCTOR'}:
            experience_value = validated_data.get("experience", "").strip()
            experience_years = None
            digits = ''.join(ch for ch in experience_value if ch.isdigit())
            if digits:
                try:
                    experience_years = int(digits)
                except ValueError:
                    experience_years = None

            summary_parts = []
            if role == 'PROVIDER':
                if validated_data.get("service_category"):
                    summary_parts.append(f"Category: {validated_data['service_category']}")
                if validated_data.get("service_name"):
                    summary_parts.append(f"Service: {validated_data['service_name']}")
            if role == 'DOCTOR':
                if validated_data.get("specialization"):
                    summary_parts.append(f"Specialization: {validated_data['specialization']}")
                if validated_data.get("hospital_name"):
                    summary_parts.append(f"Hospital/Clinic: {validated_data['hospital_name']}")
            if validated_data.get("license_number"):
                summary_parts.append(f"License: {validated_data['license_number']}")
            if validated_data.get("address"):
                summary_parts.append(f"Address: {validated_data['address']}")
            if validated_data.get("city"):
                summary_parts.append(f"City: {validated_data['city']}")

            Provider.objects.create(
                user=user,
                name=display_name,
                phone_number=user.phone,
                is_available=False,
                description='Pending admin approval' + (
                    f" | {' | '.join(summary_parts)}" if summary_parts else ''
                ),
                experience_years=experience_years,
                location=validated_data.get("city", "") or validated_data.get("address", ""),
            )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if user.role in {'PROVIDER', 'DOCTOR'} and user.approval_status != 'APPROVED':
            if user.approval_status == 'REJECTED':
                raise serializers.ValidationError("Your account was rejected by admin. Contact support or register again.")
            raise serializers.ValidationError("Your provider account is pending admin approval.")

        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField()


class AdminCreateProviderAccountSerializer(serializers.Serializer):
    provider_id = serializers.IntegerField()
    username = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=[('PROVIDER', 'Provider'), ('DOCTOR', 'Doctor')], default='PROVIDER')
