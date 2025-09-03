from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


# Create your models here.
class Dashboard(models.Model):
    class Language(models.TextChoices):
        YORUBA_LANGUAGE = "YORUBA LANGUAGE", "Yoruba Language"
        IGBO_LANGUAGE = "IGBO LANGUAGE", "Igbo Language"
        HAUSA_LANGUAGE = "HAUSA LANGUAGE", "Hausa Language"

    class LearningOption(models.TextChoices):
        start_learning = "Start Learning", "Start Learning"
        practical_skill = "Practical Skill", "Practical Skills"
        quick_practice = "Quick Practice", "Quick Practice"

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    current_language = models.CharField(
        max_length=150, choices=Language.choices, default=Language.YORUBA_LANGUAGE
    )

    complete_lesson = models.BooleanField(default=False)
    strick_count = models.PositiveIntegerField(default=0, null=True)
    learning_option = models.CharField(
        max_length=32, choices=LearningOption, default=LearningOption.start_learning
    )

    def get_current_language(self):
        return self.current_language

    def get_lesson_status(self):
        return self.complete_lesson

    def get_strick_count(self):
        return self.strick_count

    def increase_strick_count(self):
        self.strick_count += 1
        self.save()
        return self.strick_count

    def get_learning_opiton(self):
        return self.learning_option

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class LearningGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)

    class CurseDuration(models.Choices):
        one_month_course = "One-Month Course"
        two_month_course = "Two-Month Course"
        three_month_course = "Three-Month Course"
        self_learn = "Self Learning Progress"

    class LearningLevels(models.TextChoices):
        levels1 = "Basic", "Basic"
        levels2 = "Intermediate", "Intermediate"
        level3 = "Advance", "Advance"

    course_length = models.CharField(
        max_length=32, choices=CurseDuration, default=CurseDuration.one_month_course
    )
    levels = models.CharField(
        max_length=32, choices=LearningLevels, default=LearningLevels.levels1
    )

    def get_course_length(self):
        return self.course_length

    def get_levels(self):
        return self.levels

    def goto_level2(self):
        self.levels = self.LearningLevels.levels2
        self.save()
        return self.levels

    def goto_level3(self):
        self.levels = self.LearningLevels.level3
        self.save()
        return self.levels

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
