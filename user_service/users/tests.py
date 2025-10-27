# from django.test import TestCase

from django.core.mail import send_mail


send_mail(
    subject="Azure Test Email",
    message="This is a test email sent from Django application using Azure ACS.",
    from_email=None,
    recipient_list=["tsavsamuel@yahoo.com"],
)
