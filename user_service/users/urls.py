from django.urls import path
from . import views


urlpatterns = [
    path("clerk/webhook/", views.clerk_webhook, name="clerk-webhook"),
    # Service-to-service communication
    path("validate-token/", views.validate_service_token, name="validate_token"),
    path("user/<int:id>/", views.get_user_by_id, name="get_user_by_id"),
    path("validate-admin/", views.validate_admin_user, name="validate_admin_user"),
]
