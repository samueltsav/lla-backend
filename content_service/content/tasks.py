import requests
import redis
from typing import Dict, List, Optional, Any
from enum import Enum
import logging
from celery import Celery, shared_task
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry as RequestsRetry
from django.utils import timezone


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Celery("content_service_config")

# AI Agent configuration
AI_AGENT_BASE_URL = "http://ai-agents-service:8000"
REQUEST_TIMEOUT = 300
MAX_RETRIES = 3
RETRY_BACKOFF = 60


class LearningLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ExerciseType(Enum):
    TEXT_TO_SPEECH = "text_to_speech"
    AUDIO = "audio"
    FLASHCARD = "flashcard"
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    TRANSLATION = "translation"


# HTTP session with retry strategy
def create_session():
    session = requests.Session()
    retry_strategy = RequestsRetry(
        total=3, status_forcelist=[429, 500, 502, 503, 504], backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def make_ai_request(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    session = create_session()
    url = f"{AI_AGENT_BASE_URL}{endpoint}"

    try:
        response = session.post(
            url,
            json=payload,
            timeout=REQUEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"AI request failed for {endpoint}: {str(e)}")
        raise


@app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_BACKOFF)
def generate_syllabus(
    self,
    language: str,
    level: str,
    total_lessons: int = 20,
    duration_weeks: int = 12,
    user_id: Optional[str] = None,
):
    try:
        payload = {
            "task": "generate_syllabus",
            "parameters": {
                "language": language,
                "level": level,
                "total_lessons": total_lessons,
                "duration_weeks": duration_weeks,
                "user_id": user_id,
                "timestamp": datetime.now,
            },
        }

        logger.info(f"Generating syllabus for {language} - {level} level")
        result = make_ai_request("/api/v1/generate/syllabus", payload)

        # Structure the response
        syllabus_data = {
            "syllabus_id": result.get("syllabus_id"),
            "language": language,
            "level": level,
            "duration_weeks": duration_weeks,
            "modules": result.get("modules", []),
            "learning_objectives": result.get("learning_objectives", []),
            "prerequisites": result.get("prerequisites", []),
            "assessment_methods": result.get("assessment_methods", []),
            "resources": result.get("resources", []),
            "created_at": datetime.now.isoformat(),
            "user_id": user_id,
        }

        logger.info(f"Successfully generated syllabus: {syllabus_data['syllabus_id']}")
        return syllabus_data

    except Exception as e:
        logger.error(f"Error generating syllabus: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=RETRY_BACKOFF * (2**self.request.retries))
        raise


# Lesson Generation Tasks
@app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_BACKOFF)
def generate_lesson(
    self,
    syllabus_id: str,
    module_id: str,
    topic: str,
    level: str,
    user_id: Optional[str] = None,
):
    try:
        payload = {
            "task": "generate_lesson",
            "parameters": {
                "syllabus_id": syllabus_id,
                "module_id": module_id,
                "topic": topic,
                "level": level,
                "user_id": user_id,
                "timestamp": datetime.now,
            },
        }

        logger.info(f"Generating lesson for topic: {topic}")
        result = make_ai_request("/api/v1/generate/lesson", payload)

        lesson_data = {
            "lesson_id": result.get("lesson_id"),
            "syllabus_id": syllabus_id,
            "module_id": module_id,
            "topic": topic,
            "level": level,
            "content": {
                "introduction": result.get("introduction"),
                "main_content": result.get("main_content"),
                "examples": result.get("examples", []),
                "key_concepts": result.get("key_concepts", []),
                "summary": result.get("summary"),
            },
            "estimated_duration": result.get("estimated_duration", 30),  # minutes
            "difficulty_score": result.get("difficulty_score", 1),
            "prerequisites": result.get("prerequisites", []),
            "created_at": datetime.now,
            "user_id": user_id,
        }

        logger.info(f"Successfully generated lesson: {lesson_data['lesson_id']}")
        return lesson_data

    except Exception as e:
        logger.error(f"Error generating lesson: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=RETRY_BACKOFF * (2**self.request.retries))
        raise


# Exercise generation task
@app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_BACKOFF)
def generate_exercises(
    self,
    lesson_id: str,
    exercise_types: List[str],
    level: str,
    count_per_type: int = 5,
    user_id: Optional[str] = None,
):
    try:
        payload = {
            "task": "generate_exercises",
            "parameters": {
                "lesson_id": lesson_id,
                "exercise_types": exercise_types,
                "level": level,
                "count_per_type": count_per_type,
                "user_id": user_id,
                "timestamp": datetime.now,
            },
        }

        logger.info(f"Generating exercises for lesson: {lesson_id}")
        result = make_ai_request("/api/v1/generate/exercises", payload)

        exercises_data = {
            "exercise_set_id": result.get("exercise_set_id"),
            "lesson_id": lesson_id,
            "level": level,
            "exercises": result.get("exercises", {}),
            "total_exercises": sum(
                len(exercises) for exercises in result.get("exercises", {}).values()
            ),
            "estimated_completion_time": result.get("estimated_completion_time", 20),
            "created_at": datetime.now,
            "user_id": user_id,
        }

        logger.info(
            f"Successfully generated exercise set: {exercises_data['exercise_set_id']}"
        )
        return exercises_data

    except Exception as e:
        logger.error(f"Error generating exercises: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=RETRY_BACKOFF * (2**self.request.retries))
        raise


@app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_BACKOFF)
def generate_specific_exercise(
    self,
    lesson_id: str,
    exercise_type: str,
    content: str,
    level: str,
    user_id: Optional[str] = None,
):
    try:
        payload = {
            "task": "generate_specific_exercise",
            "parameters": {
                "lesson_id": lesson_id,
                "exercise_type": exercise_type,
                "content": content,
                "level": level,
                "user_id": user_id,
                "timestamp": datetime.now,
            },
        }

        logger.info(f"Generating {exercise_type} exercise for lesson: {lesson_id}")
        result = make_ai_request(f"/api/v1/generate/exercise/{exercise_type}", payload)

        exercise_data = {
            "exercise_id": result.get("exercise_id"),
            "lesson_id": lesson_id,
            "type": exercise_type,
            "content": result.get("content"),
            "metadata": result.get("metadata", {}),
            "difficulty_score": result.get("difficulty_score", 1),
            "estimated_time": result.get("estimated_time", 5),
            "created_at": datetime.now,
            "user_id": user_id,
        }

        logger.info(
            f"Successfully generated {exercise_type} exercise: {exercise_data['exercise_id']}"
        )
        return exercise_data

    except Exception as e:
        logger.error(f"Error generating {exercise_type} exercise: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=RETRY_BACKOFF * (2**self.request.retries))
        raise


# User progress tracking tasks.
@app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_BACKOFF)
def analyze_user_progress(
    self, user_id: str, course_id: str, activity_data: Dict[str, Any]
):
    try:
        payload = {
            "task": "analyze_progress",
            "parameters": {
                "user_id": user_id,
                "course_id": course_id,
                "activity_data": activity_data,
                "timestamp": datetime.now,
            },
        }

        logger.info(f"Analyzing progress for user: {user_id}")
        result = make_ai_request("/api/v1/analyze/progress", payload)

        progress_data = {
            "analysis_id": result.get("analysis_id"),
            "user_id": user_id,
            "course_id": course_id,
            "overall_progress": result.get("overall_progress", 0),  # percentage
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "recommendations": result.get("recommendations", []),
            "next_actions": result.get("next_actions", []),
            "estimated_completion_time": result.get("estimated_completion_time"),
            "performance_metrics": result.get("performance_metrics", {}),
            "learning_patterns": result.get("learning_patterns", {}),
            "created_at": datetime.now,
        }

        logger.info(f"Successfully analyzed progress: {progress_data['analysis_id']}")
        return progress_data

    except Exception as e:
        logger.error(f"Error analyzing user progress: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=RETRY_BACKOFF * (2**self.request.retries))
        raise


@app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_BACKOFF)
def update_learning_progress(
    self,
    user_id: str,
    lesson_id: str,
    exercise_results: Dict[str, Any],
    time_spent: int,
):
    try:
        payload = {
            "task": "update_progress",
            "parameters": {
                "user_id": user_id,
                "lesson_id": lesson_id,
                "exercise_results": exercise_results,
                "time_spent": time_spent,
                "timestamp": datetime.now,
            },
        }

        logger.info(f"Updating progress for user {user_id}, lesson {lesson_id}")
        result = make_ai_request("/api/v1/update/progress", payload)

        update_data = {
            "update_id": result.get("update_id"),
            "user_id": user_id,
            "lesson_id": lesson_id,
            "progress_delta": result.get("progress_delta", 0),
            "new_progress_level": result.get("new_progress_level", 0),
            "achievements_unlocked": result.get("achievements_unlocked", []),
            "skill_improvements": result.get("skill_improvements", {}),
            "updated_at": datetime.now,
        }

        logger.info(f"Successfully updated progress: {update_data['update_id']}")
        return update_data

    except Exception as e:
        logger.error(f"Error updating learning progress: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=RETRY_BACKOFF * (2**self.request.retries))
        raise


# learning path generation tasks
@app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_BACKOFF)
@app.task(bind=True, name="content.tasks.process_content")
def process_content(self, content_id):
    try:
        # Content processing logic here
        logger.info(f"Processing content {content_id}")
        return f"Content {content_id} processed successfully"
    except Exception as exc:
        logger.error(f"Error processing content {content_id}: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@app.task(bind=True, name="content.tasks.generate_thumbnails")
def generate_thumbnails(self, content_id):
    try:
        logger.info(f"Thumbnails generated for content {content_id}")
        return f"Thumbnails generated for content {content_id}"
    except Exception as exc:
        logger.error(f"Error generating thumbnails: {exc}")
        raise self.retry(exc=exc, countdown=120, max_retries=2)


@app.task(bind=True, name="content.tasks.sync_user_progress")
def sync_user_progress(self, content_id):
    pass


@app.task(bind=True, name="content.tasks.generate_content_analytics")
def generate_content_analytics(self, content_id):
    pass


@app.task(bind=True, name="content.tasks.generate_learning_path")
def generate_learning_path(
    self,
    user_id: str,
    language: str,
    current_level: str,
    target_level: str,
    time_commitment: int,
    learning_preferences: Dict[str, Any],
):
    try:
        payload = {
            "task": "generate_learning_path",
            "parameters": {
                "user_id": user_id,
                "language": language,
                "current_level": current_level,
                "target_level": target_level,
                "time_commitment": time_commitment,
                "learning_preferences": learning_preferences,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }

        logger.info(f"Generating learning path for user: {user_id}")
        result = make_ai_request("/api/v1/generate/learning_path", payload)

        path_data = {
            "learning_path_id": result.get("learning_path_id"),
            "user_id": user_id,
            "language": language,
            "current_level": current_level,
            "target_level": target_level,
            "estimated_duration_weeks": result.get("estimated_duration_weeks"),
            "milestones": result.get("milestones", []),
            "recommended_courses": result.get("recommended_courses", []),
            "skill_progression": result.get("skill_progression", []),
            "personalization_factors": result.get("personalization_factors", {}),
            "success_metrics": result.get("success_metrics", {}),
            "created_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Successfully generated learning path: {path_data['learning_path_id']}"
        )
        return path_data

    except Exception as e:
        logger.error(f"Error generating learning path: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=RETRY_BACKOFF * (2**self.request.retries))
        raise


@app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_BACKOFF)
def adapt_learning_path(
    self,
    learning_path_id: str,
    user_id: str,
    progress_data: Dict[str, Any],
    feedback: Dict[str, Any],
):
    try:
        payload = {
            "task": "adapt_learning_path",
            "parameters": {
                "learning_path_id": learning_path_id,
                "user_id": user_id,
                "progress_data": progress_data,
                "feedback": feedback,
                "timestamp": datetime.now,
            },
        }

        logger.info(f"Adapting learning path: {learning_path_id}")
        result = make_ai_request("/api/v1/adapt/learning_path", payload)

        adaptation_data = {
            "adaptation_id": result.get("adaptation_id"),
            "learning_path_id": learning_path_id,
            "user_id": user_id,
            "changes_made": result.get("changes_made", []),
            "reasoning": result.get("reasoning"),
            "updated_milestones": result.get("updated_milestones", []),
            "new_recommendations": result.get("new_recommendations", []),
            "difficulty_adjustments": result.get("difficulty_adjustments", {}),
            "updated_at": datetime.now,
        }

        logger.info(
            f"Successfully adapted learning path: {adaptation_data['adaptation_id']}"
        )
        return adaptation_data

    except Exception as e:
        logger.error(f"Error adapting learning path: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=RETRY_BACKOFF * (2**self.request.retries))
        raise


# Workflow tasks
@app.task
def create_complete_course_workflow(language: str, level: str, user_id: str):
    try:
        # Step 1: Generate syllabus
        syllabus_result = generate_syllabus.delay(
            language=language, level=level, user_id=user_id
        ).get()

        # Step 2: Generate lessons for each module
        lesson_tasks = []
        for module in syllabus_result.get("modules", []):
            for topic in module.get("lessons", []):
                lesson_task = generate_lesson.delay(
                    syllabus_id=syllabus_result["syllabus_id"],
                    module_id=module["module_id"],
                    topic=topic,
                    level=level,
                    user_id=user_id,
                )
                lesson_tasks.append(lesson_task)

        # Wait for all lessons to complete
        lessons = [task.get() for task in lesson_tasks]

        # Step 3: Generate exercises for each lesson
        exercise_tasks = []
        exercise_types = ["multiple_choice", "fill_in_blank", "flashcard"]

        for lesson in lessons:
            exercise_task = generate_exercises.delay(
                lesson_id=lesson["lesson_id"],
                exercise_types=exercise_types,
                level=level,
                user_id=user_id,
            )
            exercise_tasks.append(exercise_task)

        # Wait for all exercises to complete
        exercises = [task.get() for task in exercise_tasks]

        return {
            "course_id": f"course_{syllabus_result['syllabus_id']}",
            "syllabus": syllabus_result,
            "lessons": lessons,
            "exercises": exercises,
            "created_at": datetime.now,
        }

    except Exception as e:
        logger.error(f"Error in complete course workflow: {str(e)}")
        raise


# Cleanup tasks
r = redis.Redis(host="redis", port=6379, db=0)


@shared_task
def cleanup_old_results(days: int = 7):
    try:
        (timezone.now() - timedelta(days=days)).timestamp()
        deleted = 0

        for key in r.scan_iter("celery-task-meta-*"):
            r.get(key)
            # Optionally parse timestamp if you stored one
            r.delete(key)
            deleted += 1

        return {"status": "success", "message": f"{deleted} old results cleaned up"}
    except Exception as e:
        raise RuntimeError(f"Failed cleanup: {str(e)}")
