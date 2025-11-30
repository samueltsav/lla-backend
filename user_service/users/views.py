from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponseBadRequest
from rest_framework import status
from django.contrib.auth import get_user_model
from django.views import View
from user_service_config.django import base
from .serializers import UserSerializer
import logging
from django.views.decorators.csrf import csrf_exempt
from svix.webhooks import Webhook


logger = logging.getLogger(__name__)
User = get_user_model()

JWT_KEY = base.JWT_KEY

# Clerk Webhook
@csrf_exempt
def clerk_webhook(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    wh = Webhook(base.CLERK_WEBHOOK_SECRET)

    # MUST use raw bytes
    payload = request.body

    # MUST convert headers to plain dict
    headers = {k: v for k, v in request.headers.items()}

    try:
        event = wh.verify(payload, headers)
    except Exception as e:
        print("Webhook signature verification failed:", str(e))
        return HttpResponseBadRequest("Invalid signature")

    # ---- Parse Event ----
    event_type = event["type"]
    data = event["data"]

    if event_type == "user.created":
        id = data["id"]
        email = data.get("email_addresses", [{}])[0].get("email_address", "")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        image_url = data.get("image_url", "")

        User.objects.update_or_create(
            id=id,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "photo_url": image_url,
            },
        )

    elif event_type == "user.updated":
        id = data["id"]
        email = data.get("email_addresses", [{}])[0].get("email_address", "")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        image_url = data.get("image_url", "")

        User.objects.update_or_create(
            id=id,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "photo_url": image_url,
            },
        )
            
    elif event_type == "user.deleted":
        id = data["id"]

        try:
            User.objects.filter(id=id).delete()
            print(f"User {id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting user {id}: {str(e)}")

    return JsonResponse({"status": "ok"})


# Service-to-service views
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