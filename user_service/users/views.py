from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from django.contrib.auth import get_user_model
from django.views import View
from user_service_config.django import base
from .serializers import UserSerializer
import logging
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .clerk_sdk import ClerkSDK


logger = logging.getLogger(__name__)
User = get_user_model()

JWT_KEY = base.JWT_KEY


@csrf_exempt
def clerk_webhook(request):
    # Read raw body and signature
    body = request.body
    signature = request.headers.get("Clerk-Signature") or request.META.get(
        "HTTP_CLERK_SIGNATURE"
    )

    sdk = ClerkSDK()
    if not sdk.verify_webhook_signature(body, signature):
        return HttpResponse("Invalid signature", status=400)

    try:
        payload = json.loads(body)
    except Exception:
        return HttpResponse("Invalid payload", status=400)

    event_type = payload.get("type") or payload.get("event")
    data = payload.get("data") or payload.get("object") or {}

    # Normalize user object depending on Clerk payload shape
    user_data = data.get("user") if isinstance(data.get("user"), dict) else data
    clerk_id = user_data.get("id") or user_data.get("user_id")

    if not clerk_id:
        return HttpResponse("No user id", status=400)

    # Handle events
    if event_type in ("user.created", "users.created"):
        # create or update
        emails = user_data.get("email_addresses") or []
        email = emails[0].get("email_address") if emails else ""
        User.objects.update_or_create(
            id=clerk_id,
            defaults={
                "email": email,
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "is_active": not user_data.get("disabled", False),
            },
        )
    elif event_type in ("user.updated", "users.updated"):
        try:
            user = User.objects.get(id=clerk_id)
            emails = user_data.get("email_addresses") or []
            email = emails[0].get("email_address") if emails else user.email
            user.email = email
            user.first_name = user_data.get("first_name", user.first_name)
            user.last_name = user_data.get("last_name", user.last_name)
            user.is_active = not user_data.get("disabled", False)
            user.save()
        except User.DoesNotExist:
            # create if missing
            User.objects.create(
                id=clerk_id,
                email=(user_data.get("email") or ""),
                first_name=user_data.get("first_name", ""),
                last_name=user_data.get("last_name", ""),
                is_active=not user_data.get("disabled", False),
            )
    elif event_type in ("user.deleted", "users.deleted"):
        User.objects.filter(id=clerk_id).delete()

    # Can be extended to other events (email_verified, phone_updated, etc.)

    return HttpResponse("OK")


@api_view(["POST"])
@permission_classes([AllowAny])
def validate_service_token(request):
    token = request.data.get("token")
    if not token:
        return Response(
            {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if token != JWT_KEY:
        return Response(
            {"valid": False, "error": "Token is invalid"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Optionally return a dummy user object or service info
    return Response(
        {"valid": True, "service": "user_service"}, status=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_user_by_id(request, id):
    jwt_key = request.headers.get("X-Service-Key")
    if jwt_key != JWT_KEY:
        return Response({"error": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(id=id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([AllowAny])
def validate_admin_user(request):
    jwt_key = request.headers.get("X-Service-Key")
    if jwt_key != JWT_KEY:
        return Response({"error": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)

    id = request.data.get("id")
    try:
        user = User.objects.get(id=id)
        return Response(
            {
                "is_admin": user.is_staff or user.is_superuser,
                "is_active": user.is_active,
            },
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# Health Check
class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "ok"})