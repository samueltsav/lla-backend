from django.urls import path
from . import views
from .clerk_webhook import ClerkWebhook


urlpatterns = [
    path("clerk/webhook/", ClerkWebhook.as_view(), name="clerk-webhook"),
    path("users/<str:user_id>/", views.UserDetailView.as_view()),
]