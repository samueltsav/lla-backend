from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from .models import User
import json

from django.core.mail import send_mail

# Azure Commuication Services email test
send_mail(
    subject="Azure Test Email",
    message="This is a test email sent from Django application using Azure ACS.",
    from_email=None,
    recipient_list=["tsavsamuel@yahoo.com"],
)


# Basic tests
class ClerkWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("clerk-webhook")
        settings.CLERK_WEBHOOK_SECRET = "testsecret"

    def sign(self, payload_bytes):
        import hmac
        import hashlib

        return hmac.new(
            settings.CLERK_WEBHOOK_SECRET.encode(), payload_bytes, hashlib.sha256
        ).hexdigest()

    def test_create_user(self):
        payload = json.dumps(
            {
                "type": "user.created",
                "data": {
                    "id": "u_123",
                    "email_addresses": [{"email_address": "test@example.com"}],
                    "first_name": "T",
                    "last_name": "S",
                },
            }
        ).encode()
        sig = self.sign(payload)
        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
            **{"HTTP_CLERK_SIGNATURE": sig},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(id="u_123").exists())
