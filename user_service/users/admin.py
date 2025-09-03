from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from .forms import UserAdminChangeForm, UserAdminCreationForm

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    readonly_fields = ("uid",)
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    list_display = (
        "username",
        "email",
        "phone_number",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    list_filter = ("email", "username")
    fieldsets = (
        (None, {"fields": ("username", "email", "phone_number", "password")}),
        (
            "permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "is_active",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "phone_number",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    search_fields = ("username", "email", "phone_number")
    ordering = ("username",)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
