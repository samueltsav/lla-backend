from django.contrib import admin

from .models import (
    Language,
    Syllabus,
    Lesson,
    Exercise,
    UserLearningPath,
    UserProgress,
)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    pass


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    pass


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    pass


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    pass


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    pass


@admin.register(UserLearningPath)
class UserLearningPathAdmin(admin.ModelAdmin):
    pass
