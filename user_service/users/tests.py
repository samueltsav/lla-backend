from django.test import TestCase, Client
from django.urls import reverse
from user_service_config.django import base
import json
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from svix.webhooks import Webhook
import time


User = get_user_model()

# Azure Commuication Services email test
send_mail(
    subject="Azure Test Email",
    message="This is a test email sent from Django application using Azure ACS.",
    from_email=None,
    recipient_list=["tsavsamuel@yahoo.com"],
)


# Clerk Webhook tests
class ClerkWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("clerk-webhook")
        base.CLERK_WEBHOOK_SECRET = "testsecret"   # Svix expects raw secret

        # Create Svix webhook instance
        self.wh = Webhook(base.CLERK_WEBHOOK_SECRET)

    def test_create_user(self):
        payload_dict = {
            "type": "user.created",
            "data": {
                "user_id": "u_123",
                "email_addresses": [{"email_address": "test@example.com"}],
                "first_name": "Samuel",
                "last_name": "Tsav",
            },
        }

        payload = json.dumps(payload_dict)

        # Svix automatically generates proper signature headers
        headers = self.wh.sign(payload)

        # Django test client needs headers formatted as HTTP_*
        client_headers = {
            "HTTP_SVIX_ID": headers["svix-id"],
            "HTTP_SVIX_TIMESTAMP": headers["svix-timestamp"],
            "HTTP_SVIX_SIGNATURE": headers["svix-signature"],
        }

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
            **client_headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(id="u_123").exists())