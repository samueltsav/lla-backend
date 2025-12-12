import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from celery import shared_task
from django.utils import timezone
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry as RequestsRetry

from .models import UserMirror, Syllabus, Lesson, Exercise, UserLessonProgress, ExerciseAttempt
from content_service_config.django import base


logger = logging.getLogger(__name__)

USER_SERVICE_URL = base.USER_SERVICE_URL
AI_AGENT_BASE_URL = "http://ai-agents-service:8000"
REQUEST_TIMEOUT = 300
MAX_RETRIES = 3
RETRY_BACKOFF = 60


# Utilities
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
    try:
        response = session.post(
            f"{AI_AGENT_BASE_URL}{endpoint}",
            json=payload,
            timeout=REQUEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.exception(f"AI request failed for {endpoint}")
        raise


# User sync task
@shared_task(bind=True, max_retries=5, default_retry_delay=10)
def user_sync_event(self, event_type: str, user_id: str):
    """Sync user data from user_service"""
    url = f"{USER_SERVICE_URL}/api/users/{user_id}/"
    headers = {}
    if hasattr(base, "SERVICE_INTERNAL_TOKEN"):
        headers["Authorization"] = f"Bearer {base.SERVICE_INTERNAL_TOKEN}"
    try:
        res = requests.get(url, headers=headers, timeout=8)
        res.raise_for_status()
        data = res.json()
        UserMirror.objects.update_or_create(
            user_id=data["id"],
            defaults={
                "email": data.get("email", ""),
                "raw": data
            }
        )
        return {"synced": True, "event": event_type, "user_id": data["id"]}
    except Exception as e:
        logger.exception("Failed to sync user")
        raise self.retry(exc=e)


# Generate syllabus
@shared_task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_BACKOFF)
def generate_syllabus(self, language: str, level: str, total_lessons: int = 20, user_id: Optional[str] = None):
    try:
        payload = {
            "task": "generate_syllabus",
            "parameters": {
                "language": language,
                "level": level,
                "total_lessons": total_lessons,
                "user_id": user_id,
                "timestamp": timezone.now().isoformat(),
            }
        }
        result = make_ai_request("/syllabus/generate", payload)

        # Persist syllabus
        syllabus = Syllabus.objects.create(
            syllabus_id=result["syllabus_id"],
            language_id=language,
            level=level,
            title=result.get("title", f"{language} - {level}"),
            description=result.get("description", ""),
            estimated_hours=result.get("estimated_hours", total_lessons*1),
            is_active=True,
        )
        logger.info(f"Syllabus {syllabus.syllabus_id} created")
        return {"syllabus_id": syllabus.syllabus_id}
    except Exception as e:
        logger.exception("Failed to generate syllabus")
        raise self.retry(exc=e)


# Generate lesson
@shared_task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_BACKOFF)
def generate_lesson(self, syllabus_id: str, topic: str, user_id: Optional[str] = None):
    try:
        payload = {
            "task": "generate_lesson",
            "parameters": {
                "syllabus_id": syllabus_id,
                "topic": topic,
                "user_id": user_id,
                "timestamp": timezone.now().isoformat(),
            },
        }
        result = make_ai_request("/lesson/generate", payload)
        lesson = Lesson.objects.create(
            lesson_id=result["lesson_id"],
            syllabus_id=syllabus_id,
            lesson_number=result.get("lesson_number", 1),
            title=result.get("title", topic),
            description=result.get("description", ""),
            estimated_time_minutes=result.get("estimated_time_minutes", 30),
            learning_objectives=result.get("learning_objectives", []),
            audio_resources=result.get("audio_resources", {}),
        )
        logger.info(f"Lesson {lesson.lesson_id} created")
        return {"lesson_id": lesson.lesson_id}
    except Exception as e:
        logger.exception("Failed to generate lesson")
        raise self.retry(exc=e)


# Generate exercises
@shared_task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_BACKOFF)
def generate_exercises(self, lesson_id: str, exercise_types: List[str], level: str, user_id: Optional[str] = None):
    try:
        payload = {
            "task": "generate_exercises",
            "parameters": {
                "lesson_id": lesson_id,
                "exercise_types": exercise_types,
                "level": level,
                "user_id": user_id,
                "timestamp": timezone.now().isoformat(),
            },
        }
        result = make_ai_request("/exercises/generate", payload)

        exercises_created = []
        for ex in result.get("exercises", []):
            exercise = Exercise.objects.create(
                exercise_id=ex["exercise_id"],
                lesson_id=lesson_id,
                exercise_number=ex.get("exercise_number", 1),
                title=ex.get("title", ""),
                description=ex.get("description", ""),
                type=ex.get("type", "multiple-choice"),
                difficulty=ex.get("difficulty", "beginner"),
                estimated_time_minutes=ex.get("estimated_time_minutes", 5),
                max_points=ex.get("max_points", 10),
                content=ex.get("content", {}),
                user_id=user_id,
            )
            exercises_created.append(exercise.exercise_id)
        logger.info(f"{len(exercises_created)} exercises created for lesson {lesson_id}")
        return exercises_created
    except Exception as e:
        logger.exception("Failed to generate exercises")
        raise self.retry(exc=e)
