import random
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from .validators import ImageValidator


class UserManager(BaseUserManager):
    def generate_id(self):
        while True:
            uid = random.randint(100000, 999999)
            if not self.filter(uid=uid).exists():
                return uid

    def create_user(self, username, email, phone_number, password, **other_fields):
        if not username:
            raise ValueError(_("Please provide a valid email"))
        if not email:
            raise ValueError(_("Please provide a valid email"))
        email = self.normalize_email(email)
        if "uid" not in other_fields:
            other_fields["uid"] = self.generate_id()
        user = self.model(
            username=username,
            email=email,
            phone_number=phone_number,
            **other_fields,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, phone_number, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)
        if other_fields.get("is_staff") is not True:
            raise ValueError(_("Staff user must be assigned to is_staff=True"))
        if other_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must be assigned to is_superuser=True"))
        return self.create_user(username, email, phone_number, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
    uid = models.IntegerField(
        primary_key=True,
        unique=True,
        null=False,
        blank=False,
        editable=False,
        db_column="UID",
    )
    username = models.CharField(
        max_length=255, blank=False, null=False, unique=True, db_column="USERNAME"
    )
    email = models.EmailField(blank=False, null=False, unique=True, db_column="EMAIL")
    phone_number = models.CharField(
        max_length=32, blank=False, null=False, unique=True, db_column="PHONE NUMBER"
    )
    is_staff = models.BooleanField(default=False, db_column="STAFF")
    is_active = models.BooleanField(default=False, db_column="ACTIVE")
    first_name = models.CharField(max_length=255, db_column="FIRST NAME")
    last_name = models.CharField(max_length=255, db_column="LAST NAME")
    dob = models.DateField(null=True, blank=True, db_column="DOB")
    nationality = models.CharField(
        max_length=255, blank=True, null=True, db_column="NATIONALITY"
    )
    cor = models.CharField(max_length=255, blank=True, null=True, db_column="COR")
    photo = models.ImageField(
        upload_to="photos/",
        blank=True,
        null=True,
        validators=[ImageValidator],
        db_column="PROFILE PICTURE",
    )
    dor = models.DateTimeField(auto_now_add=True, db_column="DOR")

    updated_at = models.DateTimeField(auto_now_add=True, db_column="LAST UPDATED")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "phone_number",
    ]

    objects = UserManager()

    @property
    def id(self):
        return self.uid

    def clean(self):
        super().clean()
        if self.uid and (self.uid < 100000 or self.uid > 999999):
            raise ValidationError({"uid": "uid is not accepted"})

    def __str__(self):
        return f"{self.username} (UID: {self.uid})"

    def to_dict(self):
        return {
            "uid": self.uid,
            "username": self.username,
            "email": self.email,
        }
