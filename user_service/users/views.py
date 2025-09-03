from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
import os
from .serializers import UserServiceSerializer, MyTokenCreateSerializer
from django.http import JsonResponse
from django.views import View
from dotenv import load_dotenv

load_dotenv()

User = get_user_model()


JWT_KEY = os.getenv("JWT_KEY")


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
def get_user_by_uid(request, uid):
    jwt_key = request.headers.get("X-Service-Key")
    if jwt_key != JWT_KEY:
        return Response({"error": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(id=uid)
        serializer = UserServiceSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([AllowAny])
def validate_admin_user(request):
    jwt_key = request.headers.get("X-Service-Key")
    if jwt_key != JWT_KEY:
        return Response({"error": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)

    uid = request.data.get("uid")
    try:
        user = User.objects.get(id=uid)
        return Response(
            {
                "is_admin": user.is_staff or user.is_superuser,
                "is_active": user.is_active,
            },
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class MyTokenCreateView(TokenObtainPairView):
    serializer_class = MyTokenCreateSerializer


# Health Check
class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "ok"})
