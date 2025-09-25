from rest_framework import serializers
from .models import Language, Syllabus, Lesson, Exercise, UserProgress, UserLearningPath


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = "__all__"
        read_only_fields = ["id", "created_at", "uid"]


class SyllabusSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(
        source="language.display_name", read_only=True
    )
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Syllabus
        fields = "__all__"
        read_only_fields = ["id", "language_id", "created_at", "uid"]

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class LessonSerializer(serializers.ModelSerializer):
    exercises_count = serializers.SerializerMethodField()
    syllabus_title = serializers.CharField(source="syllabus.title", read_only=True)

    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ["id", "created_at", "uid"]

    def get_exercises_count(self, obj):
        return obj.exercises.count()


class ExerciseSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = Exercise
        fields = "__all__"
        read_only_fields = ["id", "created_at", "uid"]


class UserProgressSerializer(serializers.ModelSerializer):
    syllabus_title = serializers.CharField(source="syllabus.title", read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    exercise_title = serializers.CharField(source="exercise.title", read_only=True)

    class Meta:
        model = UserProgress
        fields = "__all__"
        read_only_fields = ["__all__"]


class UserLearningPathSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(
        source="language.display_name", read_only=True
    )
    current_syllabus_title = serializers.CharField(
        source="current_syllabus.title", read_only=True
    )

    class Meta:
        model = UserLearningPath
        fields = "__all__"
        read_only_fields = ["id", "uid"]
