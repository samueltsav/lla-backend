from django.urls import path
from . import views

# Service-to-service communication URLs
service_patterns = [
    path("validate-token/", views.validate_service_token, name="validate_token"),
    path("user/<int:uid>/", views.get_user_by_uid, name="get_user_by_uid"),
    path("validate-admin/", views.validate_admin_user, name="validate_admin_user"),
]
