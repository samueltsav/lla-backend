from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Language, Syllabus, Lesson, Exercise, UserLessonProgress, ExerciseAttempt, CardType
from .serializers import (
    LanguageSerializer,
    SyllabusSerializer,
    LessonSerializer,
    ExerciseSerializer,
    UserLessonProgressSerializer,
    ExerciseAttemptSerializer,
    CardTypeSerializer,
)
from .auth import ClerkAuthentication
import logging  
from django.views import View
from django.http import JsonResponse



logger = logging.getLogger(__name__)


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer
    authentication_classes = [ClerkAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class SyllabusViewSet(viewsets.ModelViewSet):
    serializer_class = SyllabusSerializer
    authentication_classes = [ClerkAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Syllabus.objects.filter(is_active=True)

    @action(detail=True, methods=["get"])
    def lessons(self, request, pk=None):
        syllabus = get_object_or_404(Syllabus, pk=pk)
        lessons = syllabus.lesson_set.all()  # default reverse relation
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def generate_content(self, request, pk=None):
        syllabus = get_object_or_404(Syllabus, pk=pk)
        # TODO: implement AI content generation
        return Response(
            {"message": "Content generation started", "syllabus_id": str(syllabus.syllabus_id)}
        )


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    authentication_classes = [ClerkAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.all()

    @action(detail=True, methods=["get"])
    def exercises(self, request, pk=None):
        lesson = get_object_or_404(Lesson, pk=pk)
        exercises = lesson.exercise_set.all()  # default reverse relation
        serializer = ExerciseSerializer(exercises, many=True)
        return Response(serializer.data)


class ExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseSerializer
    authentication_classes = [ClerkAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Exercise.objects.all()


class UserLessonProgressViewSet(viewsets.ModelViewSet):
    serializer_class = UserLessonProgressSerializer
    authentication_classes = [ClerkAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserLessonProgress.objects.filter(user_id=self.request.user.user_id)

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        user_progress = self.get_queryset()
        completed_lessons = user_progress.filter(status="completed").count()
        total_points = sum(progress.points_earned for progress in user_progress)
        return Response(
            {
                "completed_lessons": completed_lessons,
                "total_points": total_points,
                "user_id": request.user.user_id,
            }
        )


class ExerciseAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseAttemptSerializer
    authentication_classes = [ClerkAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExerciseAttempt.objects.filter(user_id=self.request.user.user_id)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read for all authenticated users; write only for admins."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class CardTypeViewSet(viewsets.ModelViewSet):
    queryset = CardType.objects.all()
    serializer_class = CardTypeSerializer
    authentication_classes = [ClerkAuthentication]
    permission_classes = [IsAdminOrReadOnly]


# Health Check
class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "ok"})