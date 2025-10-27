from azure.communication.email import EmailClient
from azure.core.exceptions import HttpResponseError
from django.core.mail.backends.base import BaseEmailBackend
from user_service_config.django import base


class AzureEmailBackend(BaseEmailBackend):
    """
    Custom Django email backend for Azure Communication Services Email.
    """

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        client = EmailClient.from_connection_string(base.AZURE_EMAIL_CONNECTION_STRING)
        sent_count = 0

        for message in email_messages:
            email_data = {
                "senderAddress": base.DEFAULT_FROM_EMAIL,
                "recipients": {
                    "to": [{"address": addr} for addr in message.to],
                },
                "content": {
                    "subject": message.subject,
                    "plainText": message.body,
                },
            }

            try:
                poller = client.begin_send(email_data)
                result = poller.result()
                sent_count += 1

            except HttpResponseError as e:
                print("Failed to send Email:")
                print("Status Code:", e.status_code)
                print("Error Message:", e.message)
                print("Response:", e.response.text())
                
        return sent_count
