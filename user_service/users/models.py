from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, clerk_id=None, password=None, **extra_fields):
        """
        If clerk_id is provided → Clerk user
        If not provided → Local Django user (like superuser)
        """
        if clerk_id is None:
            # Generate a UUID for local users
            clerk_id = str(uuid.uuid4())

        user = self.model(pk=clerk_id, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        return user


    def create_superuser(self, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(clerk_id=None, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User where clerk_id is the primary key."""

    id = models.CharField(primary_key=True, unique=True, max_length=255, db_index=True)
    email = models.EmailField(blank=True, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.email or str(self.id)
