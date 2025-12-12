from rest_framework import serializers
from .models import Language, Syllabus, Lesson, Exercise, UserLessonProgress, ExerciseAttempt, CardType


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class SyllabusSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(source="language.language_name", read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Syllabus
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def get_lessons_count(self, obj):
        # Use default reverse relation if no related_name
        return obj.lesson_set.count()


class LessonSerializer(serializers.ModelSerializer):
    exercises_count = serializers.SerializerMethodField()
    syllabus_title = serializers.CharField(source="syllabus.title", read_only=True)

    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def get_exercises_count(self, obj):
        return obj.exercise_set.count()


class ExerciseSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = Exercise
        fields = "__all__"
        read_only_fields = ["user_id", "created_at", "updated_at"]


class UserLessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = UserLessonProgress
        fields = "__all__"
        read_only_fields = ["user_id", "created_at", "updated_at", "last_accessed_at"]


class ExerciseAttemptSerializer(serializers.ModelSerializer):
    exercise_title = serializers.CharField(source="exercise.title", read_only=True)

    class Meta:
        model = ExerciseAttempt
        fields = "__all__"
        read_only_fields = ["user_id", "created_at"]


class CardTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardType
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
