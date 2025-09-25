from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uid = models.IntegerField()  # Reference to user in user_service

    class Meta:
        abstract = True


class Language(BaseModel):
    LANGUAGE_CHOICES = [
        ("hausa", "Hausa"),
        ("yoruba", "Yoruba"),
        ("igbo", "Igbo"),
        ("swahili", "Swahili"),
    ]

    name = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, unique=True)
    language_id = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "languages"

    def __str__(self):
        return self.display_name


class Syllabus(BaseModel):
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="syllabi"
    )
    title = models.CharField(max_length=200)
    syllabus_id = models.UUIDField(default=uuid.uuid4, editable=False)
    description = models.TextField()
    level = models.CharField(
        max_length=20,
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
    )
    total_lessons = models.IntegerField(default=0)
    duration_weeks = models.IntegerField(default=1)

    class Meta:
        db_table = "syllabi"
        verbose_name_plural = "syllabi"

    def __str__(self):
        return f"{self.language.display_name} - {self.title}"


class Lesson(BaseModel):
    syllabus = models.ForeignKey(
        Syllabus, on_delete=models.CASCADE, related_name="lessons"
    )
    topic = models.CharField(max_length=200)
    lessson_id = models.UUIDField(default=uuid.uuid4, editable=False)
    description = models.TextField()
    content = models.JSONField(default=dict)  # AI-generated lesson content
    order = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lessons"
        ordering = ["order"]

    def __str__(self):
        return f"{self.syllabus.title} - {self.title}"


class Exercise(BaseModel):
    """Exercises for lessons"""

    EXERCISE_TYPES = [
        ("text_to_speech", "Text-To-Speech"),
        ("audio", "Audio Exercise"),
        ("flashcard", "Flashcard"),
        ("multiple_choice", "Multiple Choice"),
        ("fill_blank", "Fill-in-the-Blank"),
        ("translation", "Translation"),
    ]

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="exercises"
    )
    topic = models.CharField(max_length=200)
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    content = models.JSONField(default=dict)  # Exercise data
    audio_url = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=10)

    class Meta:
        db_table = "exercises"
        ordering = ["order"]

    def __str__(self):
        return f"{self.lesson.topic} - {self.topic}"


class UserProgress(BaseModel):
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, null=True, blank=True
    )
    completed = models.BooleanField(default=False)
    score = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    completion_date = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.IntegerField(default=0)

    class Meta:
        db_table = "user_progress"
        unique_together = [["uid", "syllabus", "lesson", "exercise"]]

    def __str__(self):
        return f"User {self.uid} - {self.syllabus.title}"


class UserLearningPath(BaseModel):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    current_syllabus = models.ForeignKey(
        Syllabus, on_delete=models.SET_NULL, null=True, blank=True
    )
    proficiency_level = models.CharField(
        max_length=20,
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
        default="beginner",
    )
    daily_commitment_minutes = models.IntegerField(default=30)
    last_activity_date = models.DateField(auto_now=True)
    total_points = models.IntegerField(default=0)

    class Meta:
        db_table = "user_learning_paths"
        unique_together = [["uid", "language"]]

    def __str__(self):
        return f"User {self.uid} - {self.language.language_id}"
