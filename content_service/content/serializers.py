from rest_framework import serializers
from .models import Language, Syllabus, Lesson, Exercise, UserProgress, UserLearningPath


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = [
            "id",
            "name",
            "display_name",
            "description",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "uid"]


class SyllabusSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(
        source="language.display_name", read_only=True
    )
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Syllabus
        fields = [
            "id",
            "language",
            "language_name",
            "title",
            "description",
            "level",
            "total_lessons",
            "lessons_count",
            "estimated_duration_weeks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "uid"]

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class LessonSerializer(serializers.ModelSerializer):
    exercises_count = serializers.SerializerMethodField()
    syllabus_title = serializers.CharField(source="syllabus.title", read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "syllabus",
            "syllabus_title",
            "title",
            "description",
            "content",
            "order",
            "duration_minutes",
            "exercises_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "uid"]

    def get_exercises_count(self, obj):
        return obj.exercises.count()


class ExerciseSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = Exercise
        fields = [
            "id",
            "lesson",
            "lesson_title",
            "title",
            "exercise_type",
            "content",
            "audio_url",
            "order",
            "points",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "uid"]


class UserProgressSerializer(serializers.ModelSerializer):
    syllabus_title = serializers.CharField(source="syllabus.title", read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    exercise_title = serializers.CharField(source="exercise.title", read_only=True)

    class Meta:
        model = UserProgress
        fields = [
            "id",
            "syllabus",
            "syllabus_title",
            "lesson",
            "lesson_title",
            "exercise",
            "exercise_title",
            "completed",
            "score",
            "completion_date",
            "time_spent_seconds",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "uid"]


class UserLearningPathSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(
        source="language.display_name", read_only=True
    )
    current_syllabus_title = serializers.CharField(
        source="current_syllabus.title", read_only=True
    )

    class Meta:
        model = UserLearningPath
        fields = [
            "id",
            "language",
            "language_name",
            "current_syllabus",
            "current_syllabus_title",
            "proficiency_level",
            "daily_goal_minutes",
            "streak_days",
            "last_activity_date",
            "total_points",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "uid"]
