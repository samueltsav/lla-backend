from django.contrib import admin
from .models import (
    Language,
    Syllabus,
    Lesson,
    Exercise,
    UserLessonProgress,
    ExerciseAttempt,
    CardType,
)

@admin.register(CardType)
class CardTypeAdmin(admin.ModelAdmin):
    list_display = ("type_id", "type_name", "supports_audio", "supports_images", "supports_hints")
    search_fields = ("type_id", "type_name")
    list_filter = ("supports_audio", "supports_images", "supports_hints")


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("language_id", "language_name", "iso_code", "is_active")
    search_fields = ("language_name", "iso_code")


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = ("syllabus_id", "language", "level", "title", "is_active")
    search_fields = ("title",)
    list_filter = ("level", "is_active", "language")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("lesson_id", "syllabus", "lesson_number", "title")
    search_fields = ("title",)
    list_filter = ("syllabus",)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("exercise_id", "lesson", "title", "type", "difficulty")
    list_filter = ("difficulty", "type")


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user_id", "lesson", "status", "percent_complete")


@admin.register(ExerciseAttempt)
class ExerciseAttemptAdmin(admin.ModelAdmin):
    list_display = ("attempt_id", "user_id", "exercise", "score", "submitted_at")
