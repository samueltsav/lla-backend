from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r"languages", views.LanguageViewSet, basename="language")
router.register(r"syllabi", views.SyllabusViewSet, basename="syllabus")
router.register(r"lessons", views.LessonViewSet, basename="lesson")
router.register(r"exercises", views.ExerciseViewSet, basename="exercise")
router.register(r"lesson_progress", views.UserLessonProgressViewSet, basename="user-progress")
router.register(r"exercise_attempts", views.ExerciseAttemptViewSet, basename="exercise-attempt")
router.register(r"cardtype", views.CardTypeViewSet, basename="progress")

urlpatterns = [
    path("", include(router.urls)),
]
