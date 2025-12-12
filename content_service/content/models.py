from django.db import models
import uuid
from django.core.exceptions import ValidationError



# ABSTRACT USER MIRROR MODEL
class UserMirror(models.Model):
    user_id = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(max_length=255, blank=True, null=True, db_index=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.email or self.user_id


# CONTENT MODELS
class Language(models.Model):
    LANGUAGE_CHOICES = [
        ("hausa", "Hausa"),
        ("yoruba", "Yoruba"),
        ("igbo", "Igbo"),
        ("swahili", "Swahili"),
    ]

    language_id = models.CharField(max_length=50, primary_key=True)
    language_name = models.CharField(max_length=100, choices=LANGUAGE_CHOICES, unique=True)
    iso_code = models.CharField(max_length=10)
    flag_emoji = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "languages"
        ordering = ["-is_active", "updated_at"]


class Syllabus(models.Model):
    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    syllabus_id = models.CharField(max_length=50, primary_key=True)
    language = models.ForeignKey(Language, on_delete=models.PROTECT, db_index=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    estimated_hours = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "syllabi"
        verbose_name_plural = "Syllabi"
        ordering = ["-is_active", "created_at"]


class Lesson(models.Model):
    lesson_id = models.CharField(max_length=50, primary_key=True)
    syllabus = models.ForeignKey(Syllabus, on_delete=models.PROTECT, db_index=True)
    lesson_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    estimated_time_minutes = models.IntegerField()
    learning_objectives = models.JSONField(default=list)
    audio_resources = models.JSONField(default=dict, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lessons"
        constraints = [
            models.UniqueConstraint(fields=["syllabus", "lesson_number"], name="unique_syllabus_lesson_number")
        ]
        ordering = ["syllabus", "lesson_number"]


# USER-SPECIFIC MODELS
class Exercise(UserMirror):
    TYPE_CHOICES = [
        ("image-description", "Image Description"),
        ("multiple-choice", "Multiple Choice"),
        ("translation", "Translation"),
        ("fill-in-the-blank", "Fill in the Blank"),
        ("matching-pairs", "Matching Pairs"),
    ]

    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    exercise_id = models.CharField(max_length=50, primary_key=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, db_index=True)
    exercise_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    estimated_time_minutes = models.IntegerField()
    max_points = models.IntegerField()
    content = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "exercises"
        constraints = [
            models.UniqueConstraint(fields=["user_id", "lesson", "exercise_number"], name="unique_user_lesson_exercise_number")
        ]
        ordering = ["user_id", "lesson", "exercise_number"]


class UserLessonProgress(UserMirror):
    STATUS_CHOICES = [
        ("not-started", "Not Started"),
        ("in-progress", "In Progress"),
        ("completed", "Completed"),
    ]
    progress_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not-started")
    completed_exercises = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    percent_complete = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lesson_progress"
        constraints = [
            models.UniqueConstraint(fields=["user_id", "lesson"], name="unique_user_lesson")
        ]
        ordering = ["user_id", "status", "last_accessed_at"]


class ExerciseAttempt(UserMirror):
    attempt_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, db_index=True)
    score = models.IntegerField()
    max_score = models.IntegerField()
    points_earned = models.IntegerField()
    time_spent_seconds = models.IntegerField()
    answers = models.JSONField()
    results = models.JSONField()
    started_at = models.DateTimeField()
    submitted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exercise_attempts"
        ordering = ["user_id", "-submitted_at"]

    def clean(self):
        """Ensure exercise.user_id matches attempt.user_id."""
        if self.exercise.user_id != self.user_id:
            raise ValidationError("Inconsistent user_id!")


# OTHER CONTENT MODELS
class CardType(models.Model):
    """Registry of available exercise card types"""

    TYPE_CHOICES = [
        ("image-description", "Image Description"),
        ("multiple-choice", "Multiple Choice"),
        ("translation", "Translation"),
        ("fill-in-the-blank", "Fill in the Blank"),
        ("matching-pairs", "Matching Pairs"),
    ]

    type_id = models.CharField(max_length=50, primary_key=True, choices=TYPE_CHOICES)
    type_name = models.CharField(max_length=100)
    description = models.TextField()
    supports_audio = models.BooleanField(default=False)
    supports_images = models.BooleanField(default=False)
    supports_hints = models.BooleanField(default=False)
    frontend_component = models.CharField(max_length=100)
    fields_schema = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "card_types"
        ordering = ["type_name"]
