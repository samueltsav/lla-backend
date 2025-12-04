from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Language, Syllabus, Lesson, Exercise, UserProgress, UserLearningPath
from .serializers import (
    LanguageSerializer,
    SyllabusSerializer,
    LessonSerializer,
    ExerciseSerializer,
    UserProgressSerializer,
    UserLearningPathSerializer,
)
from .auth import JWTAuthentication

from django.views import View

from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import get_user_model
from content_service_config.django import base
import logging
from django.views.decorators.csrf import csrf_exempt
from svix.webhooks import Webhook


logger = logging.getLogger(__name__)
User = get_user_model()

class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(id=self.request.user.id)


class SyllabusViewSet(viewsets.ModelViewSet):
    serializer_class = SyllabusSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can see their own syllabi and public ones
        if hasattr(self.request.user, "is_staff") and self.request.user.is_staff:
            return Syllabus.objects.all()
        return Syllabus.objects.filter(id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(id=self.request.user.id)

    @action(detail=True, methods=["get"])
    def lessons(self, request, pk=None):
        syllabus = get_object_or_404(Syllabus, pk=pk)
        lessons = syllabus.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def generate_content(self, request, pk=None):
        """
        Trigger AI content generation for syllabus
        Only admins or syllabus owners can do this
        """
        syllabus = get_object_or_404(Syllabus, pk=pk)

        # Check permissions
        if syllabus.id != request.user.id and not self.request.user.is_staff:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        # TODO: Implement AI content generation logic
        # This would trigger your AI agents to generate lessons and exercises

        return Response(
            {"message": "Content generation started", "syllabus_id": str(syllabus.id)}
        )


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.filter(id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(id=self.request.user.id)

    @action(detail=True, methods=["get"])
    def exercises(self, request, pk=None):
        """Get all exercises for a lesson"""
        lesson = get_object_or_404(Lesson, pk=pk, id=request.user.id)
        exercises = lesson.exercises.all()
        serializer = ExerciseSerializer(exercises, many=True)
        return Response(serializer.data)


class ExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Exercise.objects.filter(id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(id=self.request.user.id)


class UserProgressViewSet(viewsets.ModelViewSet):
    serializer_class = UserProgressSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProgress.objects.filter(id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(id=self.request.user.id)

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        """Get user progress dashboard data"""
        user_progress = self.get_queryset()
        completed_lessons = user_progress.filter(
            lesson__isnull=False, completed=True
        ).count()
        completed_exercises = user_progress.filter(
            exercise__isnull=False, completed=True
        ).count()
        total_points = sum(
            progress.score for progress in user_progress if progress.completed
        )

        return Response(
            {
                "completed_lessons": completed_lessons,
                "completed_exercises": completed_exercises,
                "total_points": total_points,
                "id": request.user.id,
            }
        )


class UserLearningPathViewSet(viewsets.ModelViewSet):
    serializer_class = UserLearningPathSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserLearningPath.objects.filter(id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(id=self.request.user.id)


# Clerk Webhook view
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


# Health Check
class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "ok"})