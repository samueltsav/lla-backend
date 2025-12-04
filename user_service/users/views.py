from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import get_user_model
from django.views import View
from user_service_config.django import base
import logging
from django.views.decorators.csrf import csrf_exempt
from svix.webhooks import Webhook


logger = logging.getLogger(__name__)
User = get_user_model()


# Clerk Webhook view
@csrf_exempt
def clerk_webhook(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    wh = Webhook(base.CLERK_WEBHOOK_SECRET)

    # MUST use raw bytes
    payload = request.body

    # MUST convert headers to plain dict
    headers = {k: v for k, v in request.headers.items()}

    try:
        event = wh.verify(payload, headers)
    except Exception as e:
        print("Webhook signature verification failed:", str(e))
        return HttpResponseBadRequest("Invalid signature")

    # ---- Parse Event ----
    event_type = event["type"]
    data = event["data"]

    if event_type == "user.created":
        id = data["id"]
        email = data.get("email_addresses", [{}])[0].get("email_address", "")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        image_url = data.get("image_url", "")

        User.objects.update_or_create(
            id=id,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "photo_url": image_url,
            },
        )

    elif event_type == "user.updated":
        id = data["id"]
        email = data.get("email_addresses", [{}])[0].get("email_address", "")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        image_url = data.get("image_url", "")

        User.objects.update_or_create(
            id=id,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "photo_url": image_url,
            },
        )
            
    elif event_type == "user.deleted":
        id = data["id"]

        try:
            User.objects.filter(id=id).delete()
            print(f"User {id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting user {id}: {str(e)}")

    return JsonResponse({"status": "ok"})


# Health Check
class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "ok"})