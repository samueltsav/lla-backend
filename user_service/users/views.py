from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer
from user_service_config.django import base
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer


User = get_user_model()

# User API for service-to-service communication
class UserDetailView(APIView):
    """
    Returns user details for internal service requests only.
    """
    def get(self, request, user_id):
        # Verify service-to-service token
        auth_header = request.headers.get("Authorization", "")
        expected_token = f"Bearer {base.SERVICE_INTERNAL_TOKEN}"
        if auth_header != expected_token:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        user = get_object_or_404(User, user_id=user_id)
        return Response(UserSerializer(user).data)


# Health Check
class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "ok"})