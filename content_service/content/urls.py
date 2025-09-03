from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r"languages", views.LanguageViewSet)
router.register(r"syllabi", views.SyllabusViewSet, basename="syllabus")
router.register(r"lessons", views.LessonViewSet, basename="lesson")
router.register(r"exercises", views.ExerciseViewSet, basename="exercise")
router.register(r"progress", views.UserProgressViewSet, basename="progress")
router.register(
    r"learning-paths", views.UserLearningPathViewSet, basename="learningpath"
)

urlpatterns = [
    path("", include(router.urls)),
]