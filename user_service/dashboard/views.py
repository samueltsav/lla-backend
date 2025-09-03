from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Dashboard, LearningGoal
from .serializer import DashboardContentSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.dispatch import receiver
from django.db.models.signals import post_save
from users.models import User


class DashboardApiView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="GetDashboardData",
        summary="Retrieve User Dashboard Data",
        description="This endpoint retrieves data from the dashboard model and Learning Goal model.",
        responses={
            200: OpenApiResponse(
                description="Success, returns the user dashboard data.",
                response=DashboardContentSerializer,
            ),
            404: OpenApiResponse(
                description="Dashboard not found for the authenticated user."
            ),
        },
    )
    def get(self, request):
        try:
            user_dashboard = Dashboard.objects.get(user=request.user)
        except Dashboard.DoesNotExist:
            return Response(
                "Dashboard not found for the authenticated user.",
                status=status.HTTP_404_NOT_FOUND,
            )

        current_language = user_dashboard.get_current_language()
        lesson_status = user_dashboard.get_lesson_status()
        learning_option = user_dashboard.get_learning_opiton()

        combined_data = {
            "user": user_dashboard,
            "current_language": current_language,
            "lesson_status": lesson_status,
            "learning_option": learning_option,
        }

        serializer = DashboardContentSerializer(combined_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="Updata Dashboard Or LearningGoal",
        summary="Update Dashboard or Learning Goal",
        description="Update dashboard or learning goal for the authenticated user.",
        request=DashboardContentSerializer,
        responses={
            200: DashboardContentSerializer,
            400: OpenApiResponse(
                description="Bad Request", examples={"error": "Validation errors"}
            ),
        },
    )
    def post(self, request):
        serializer = DashboardContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Save the instance with the user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Dashboard.objects.create(user=instance)
            LearningGoal.objects.create(user=instance)
