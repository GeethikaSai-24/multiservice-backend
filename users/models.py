from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role='USER', **extra_fields):
        if not email:
            raise ValueError('Users must have an email')
        if not username:
            raise ValueError('Users must have a username')

        email = self.normalize_email(email)
        approval_status = extra_fields.pop('approval_status', None)
        if approval_status is None:
            approval_status = 'PENDING' if role in {'PROVIDER', 'DOCTOR'} else 'APPROVED'

        user = self.model(
            username=username,
            email=email,
            role=role,
            approval_status=approval_status,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('approval_status', 'APPROVED')

        return self.create_user(username, email, password, role='ADMIN', **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('USER', 'User'),
        ('PROVIDER', 'Provider'),
        ('DOCTOR', 'Doctor'),
        ('ADMIN', 'Admin'),
    )

    APPROVAL_CHOICES = (
        ('APPROVED', 'Approved'),
        ('PENDING', 'Pending'),
        ('REJECTED', 'Rejected'),
    )

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default='APPROVED',
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
